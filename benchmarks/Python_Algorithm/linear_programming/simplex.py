"""
Python implementation of the simplex algorithm for solving linear programs in
tabular form with
- `>=`, `<=`, and `=` constraints and
- each variable `x1, x2, ...>= 0`.

See https://gist.github.com/imengus/f9619a568f7da5bc74eaf20169a24d98 for how to
convert linear programs to simplex tableaus, and the steps taken in the simplex
algorithm.

Resources:
https://en.wikipedia.org/wiki/Simplex_algorithm
https://tinyurl.com/simplex4beginners
"""

import argparse
import sys
from typing import Any

import numpy as np


class Tableau:
    """Operate on simplex tableaus

    >>> Tableau(np.array([[-1,-1,0,0,1],[1,3,1,0,4],[3,1,0,1,4]]), 2, 2)
    Traceback (most recent call last):
    ...
    TypeError: Tableau must have type float64

    >>> Tableau(np.array([[-1,-1,0,0,-1],[1,3,1,0,4],[3,1,0,1,4.]]), 2, 2)
    Traceback (most recent call last):
    ...
    ValueError: RHS must be > 0

    >>> Tableau(np.array([[-1,-1,0,0,1],[1,3,1,0,4],[3,1,0,1,4.]]), -2, 2)
    Traceback (most recent call last):
    ...
    ValueError: number of (artificial) variables must be a natural number
    """

    # Max iteration number to prevent cycling
    maxiter = 1000 # Increased for larger problems

    def __init__(
        self, tableau: np.ndarray, n_vars: int, n_artificial_vars: int
    ) -> None:
        if tableau.dtype != "float64":
            raise TypeError("Tableau must have type float64")

        # Check if RHS is negative
        if not (tableau[1:, -1] >= 0).all():
            raise ValueError("RHS must be > 0")

        if n_vars < 1 or n_artificial_vars < 0:
            raise ValueError(
                "number of (artificial) variables must be a natural number"
            )

        self.tableau = tableau
        self.n_rows, n_cols = tableau.shape

        # Number of decision variables x1, x2, x3...
        self.n_vars, self.n_artificial_vars = n_vars, n_artificial_vars

        # 2 if there are >= or == constraints (nonstandard), 1 otherwise (std)
        self.n_stages = (self.n_artificial_vars > 0) + 1

        # Number of slack variables added to make inequalities into equalities
        self.n_slack = n_cols - self.n_vars - self.n_artificial_vars - 1

        # Objectives for each stage
        self.objectives = ["max"]

        # In two stage simplex, first minimise then maximise
        if self.n_artificial_vars:
            self.objectives.append("min")

        self.col_titles = self.generate_col_titles()

        # Index of current pivot row and column
        self.row_idx = None
        self.col_idx = None

        # Does objective row only contain (non)-negative values?
        self.stop_iter = False

    def generate_col_titles(self) -> list[str]:
        """Generate column titles for tableau of specific dimensions

        >>> Tableau(np.array([[-1,-1,0,0,1],[1,3,1,0,4],[3,1,0,1,4.]]),
        ... 2, 0).generate_col_titles()
        ['x1', 'x2', 's1', 's2', 'RHS']

        >>> Tableau(np.array([[-1,-1,0,0,1],[1,3,1,0,4],[3,1,0,1,4.]]),
        ... 2, 2).generate_col_titles()
        Traceback (most recent call last):
        ...
        ValueError: number of (artificial) variables must be a natural number
        """
        args = (self.n_vars, self.n_slack)

        # decision | slack
        string_starts = ["x", "s"]
        titles = []
        for i in range(2):
            for j in range(args[i]):
                titles.append(string_starts[i] + str(j + 1))
        titles.append("RHS")
        return titles

    def find_pivot(self) -> tuple[Any, Any]:
        """Finds the pivot row and column.
        >>> tuple(int(x) for x in Tableau(np.array([[-2,1,0,0,0], [3,1,1,0,6],
        ... [1,2,0,1,7.]]), 2, 0).find_pivot())
        (1, 0)
        """
        objective = self.objectives[-1]

        # Find entries of highest magnitude in objective rows
        sign = (objective == "min") - (objective == "max")
        obj_row = self.tableau[0, :self.n_vars + self.n_slack]
        
        # Check if optimal
        if (sign * obj_row <= 1e-9).all():
            self.stop_iter = True
            return 0, 0
        
        col_idx = np.argmax(sign * obj_row)

        # Pivot row is chosen as having the lowest quotient when elements of
        # the pivot column divide the right-hand side

        # Slice excluding the objective rows
        s = slice(self.n_stages, self.n_rows)

        # RHS
        dividend = self.tableau[s, -1]

        # Elements of pivot column within slice
        divisor = self.tableau[s, col_idx]

        # Array filled with nans
        nans = np.full(self.n_rows - self.n_stages, np.inf)

        # If element in pivot column is greater than zero, return
        # quotient or nan otherwise
        quotients = np.divide(dividend, divisor, out=nans, where=divisor > 1e-9)

        # Arg of minimum quotient excluding the nan values. n_stages is added
        # to compensate for earlier exclusion of objective columns
        if np.isinf(quotients).all():
            # Unbounded solution
            raise ValueError("Linear program is unbounded.")
        
        row_idx = np.argmin(quotients) + self.n_stages
        return row_idx, col_idx

    def pivot(self, row_idx: int, col_idx: int) -> np.ndarray:
        """Pivots on value on the intersection of pivot row and column.

        >>> Tableau(np.array([[-2,-3,0,0,0],[1,3,1,0,4],[3,1,0,1,4.]]),
        ... 2, 0).pivot(1, 1).tolist()
        ... # doctest: +NORMALIZE_WHITESPACE
        [[ -1.0, 0.0, 1.0, 0.0, 4.0],
         [0.3333333333333333, 1.0, 0.3333333333333333, 0.0, 1.3333333333333333],
         [2.6666666666666665, 0.0, -0.3333333333333333, 1.0, -0.33333333333333326]]
        """
        piv_val = self.tableau[row_idx, col_idx]
        piv_row = self.tableau[row_idx] / piv_val

        self.tableau[row_idx] = piv_row
        
        for i in range(self.n_rows):
            if i != row_idx:
                self.tableau[i] -= self.tableau[i, col_idx] * piv_row
        
        return self.tableau

    def change_stage(self) -> np.ndarray:
        """Exits first phase of the two-stage method by deleting artificial
        rows and columns, or completes the algorithm if exiting the standard
        case.

        >>> Tableau(np.array([
        ... [3, 3, -1, -1, 0, 0, 4],
        ... [2, 1, 0, 0, 0, 0, 0.],
        ... [1, 2, -1, 0, 1, 0, 2],
        ... [2, 1, 0, -1, 0, 1, 2]
        ... ]), 2, 2).change_stage().tolist()
        ... # doctest: +NORMALIZE_WHITESPACE
        [[2.0, 1.0, 0.0, 0.0, 0.0],
         [1.0, 2.0, -1.0, 1.0, 2.0],
         [2.0, 1.0, 0.0, -1.0, 2.0]]
        """
        # Objective of original objective row remains
        self.objectives.pop()

        if not self.objectives:
            return self.tableau

        # Slice containing ids for artificial columns
        s = slice(self.n_vars + self.n_slack, -1)

        # Delete the artificial variable columns
        self.tableau = np.delete(self.tableau, s, axis=1)

        # Delete the objective row of the first stage
        self.tableau = np.delete(self.tableau, 0, axis=0)

        self.n_stages = 1
        self.n_rows -= 1
        self.n_artificial_vars = 0
        self.stop_iter = False
        return self.tableau

    def run_simplex(self) -> dict[Any, Any]:
        """Operate on tableau until objective function cannot be
        improved further.

        # Standard linear program:
        Max:  x1 +  x2
        ST:   x1 + 3x2 <= 4
             3x1 +  x2 <= 4
        >>> {key: float(value) for key, value in Tableau(np.array([[-1,-1,0,0,0],
        ... [1,3,1,0,4],[3,1,0,1,4.]]), 2, 0).run_simplex().items()}
        {'P': 2.0, 'x1': 1.0, 'x2': 1.0}
        """
        # Stop simplex algorithm from cycling.
        for _ in range(Tableau.maxiter):
            # Completion of each stage removes an objective. If both stages
            # are complete, then no objectives are left
            if not self.objectives:
                # Find the values of each variable at optimal solution
                return self.interpret_tableau()

            row_idx, col_idx = self.find_pivot()

            # If there are no more negative values in objective row
            if self.stop_iter:
                # Infeasible if artificial objective is non-zero
                if self.n_stages == 2 and abs(self.tableau[0, -1]) > 1e-9:
                    raise ValueError("Linear program is infeasible.")
                # Delete artificial variable columns and rows. Update attributes
                self.tableau = self.change_stage()
            else:
                self.tableau = self.pivot(row_idx, col_idx)
        
        print("Warning: Maximum iterations reached. Algorithm may be cycling.", file=sys.stderr)
        return {}

    def interpret_tableau(self) -> dict[str, float]:
        """Given the final tableau, add the corresponding values of the basic
        decision variables to the `output_dict`
        >>> {key: float(value) for key, value in Tableau(np.array([
        ... [0,0,0.875,0.375,5],
        ... [0,1,0.375,-0.125,1],
        ... [1,0,-0.125,0.375,1]
        ... ]),2, 0).interpret_tableau().items()}
        {'P': 5.0, 'x1': 1.0, 'x2': 1.0}
        """
        # P = RHS of final tableau
        output_dict = {"P": abs(self.tableau[0, -1])}

        for i in range(self.n_vars):
            col = self.tableau[1:, i]
            # Check for exactly one '1' and the rest (near) zero
            is_basic = (np.count_nonzero(np.isclose(col, 1)) == 1) and \
                       (np.count_nonzero(np.isclose(col, 0)) == len(col) - 1)
            
            if is_basic:
                row_idx = np.where(np.isclose(self.tableau[:, i], 1))[0][0]
                rhs_val = self.tableau[row_idx, -1]
                output_dict[self.col_titles[i]] = rhs_val
        return output_dict


def generate_random_problem(
    n_vars: int, n_constraints: int
) -> tuple[np.ndarray, int, int]:
    """
    Generates a random, standard-form maximization LP problem tableau.
    The generated problem is likely to be feasible and bounded.
    """
    # A: constraint coefficients
    A = np.random.rand(n_constraints, n_vars) * 10

    # b: RHS of constraints (all positive)
    b = np.random.rand(n_constraints) * 50 + 10

    # c: objective function coefficients (all positive for maximization)
    c = np.random.rand(n_vars) * 5

    # --- Assemble the tableau ---
    tableau = np.zeros(
        (n_constraints + 1, n_vars + n_constraints + 1), dtype=np.float64
    )

    # Objective row (P - c*x = 0  =>  [-c, 0..., 0])
    tableau[0, :n_vars] = -c

    # Constraint rows (A*x + s = b  =>  [A, I, b])
    tableau[1:, :n_vars] = A
    tableau[1:, n_vars:-1] = np.identity(n_constraints)
    tableau[1:, -1] = b

    # Return tableau, n_vars, and 0 artificial variables for standard form
    return tableau, n_vars, 0


def main(size: str) -> None:
    """Sets up and solves a linear program of a specified size."""
    print(f"Running simplex algorithm for '{size}' problem size.")
    
    tableau_arr = np.array([])
    n_vars = 0
    n_artificial_vars = 0

    if size == "small":
        # A moderately sized, randomly generated problem.
        num_variables = 15
        num_constraints = 15
        print(
            f"Generating a random problem with {num_variables} variables and "
            f"{num_constraints} constraints."
        )
        tableau_arr, n_vars, n_artificial_vars = generate_random_problem(
            num_variables, num_constraints
        )

    elif size == "large":
        # A larger, randomly generated problem for performance testing.
        num_variables = 200
        num_constraints = 200
        print(
            f"Generating a random problem with {num_variables} variables and "
            f"{num_constraints} constraints."
        )
        tableau_arr, n_vars, n_artificial_vars = generate_random_problem(
            num_variables, num_constraints
        )

    # Create and solve the tableau
    try:
        problem = Tableau(tableau_arr, n_vars, n_artificial_vars)
        solution = problem.run_simplex()

        print("\n--- Solution ---")
        if solution:
            # For large problems, don't print all variables to avoid clutter
            print(f"Optimal value P = {solution.get('P', 'N/A'):.4f}")
            if len(solution) < 15: # Print variables only if there are a few
                 for key, value in solution.items():
                    if key != 'P':
                        print(f"{key}: {value:.4f}")
            else:
                print("(Solution for individual variables is too large to display)")
        else:
            print("No solution found or algorithm did not converge.")
        print("----------------\n")

    except (ValueError, TypeError, IndexError) as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    # The original script used doctest. To run tests, you can use:
    # import doctest
    # doctest.testmod(verbose=True)
    # For benchmarking, we use argparse to select a problem size.

    parser = argparse.ArgumentParser(
        description="""
        Python implementation of the simplex algorithm for solving linear programs.
        This script can be run with different problem sizes for performance testing.
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--size",
        choices=["small", "large"],
        required=True,
        help=(
            "Select the size of the linear program to solve:\n"
            "'small': A randomly generated 15-variable, 15-constraint problem.\n"
            "'large': A randomly generated 200-variable, 200-constraint problem."
        ),
    )

    args = parser.parse_args()
    main(args.size)
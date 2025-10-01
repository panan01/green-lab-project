"""
Jacobi Iteration Method - https://en.wikipedia.org/wiki/Jacobi_method
"""

from __future__ import annotations

import argparse
import sys
import time

import numpy as np
from numpy import float32, floating
from numpy.typing import NDArray


# Method to find solution of system of linear equations
def jacobi_iteration_method(
    coefficient_matrix: NDArray[floating],
    constant_matrix: NDArray[floating],
    init_val: list[float],
    iterations: int,
) -> list[float]:
    """
    Jacobi Iteration Method:
    An iterative algorithm to determine the solutions of a strictly diagonally dominant
    system of linear equations.

    Example system:
    4x1 +  x2 +  x3 =  2
      x1 + 5x2 + 2x3 = -6
      x1 + 2x2 + 4x3 = -4

    x_init = [0.5, -0.5 , -0.5]

    Examples:
    >>> coefficient = np.array([[4, 1, 1], [1, 5, 2], [1, 2, 4]])
    >>> constant = np.array([[2], [-6], [-4]])
    >>> init_val = [0.5, -0.5, -0.5]
    >>> iterations = 3
    >>> result = jacobi_iteration_method(coefficient, constant, init_val, iterations)
    >>> np.allclose(result, [0.909375, -1.14375, -0.7484375])
    True
    """
    rows1, cols1 = coefficient_matrix.shape
    rows2, cols2 = constant_matrix.shape

    if rows1 != cols1:
        msg = f"Coefficient matrix dimensions must be nxn but received {rows1}x{cols1}"
        raise ValueError(msg)

    if cols2 != 1:
        msg = f"Constant matrix must be nx1 but received {rows2}x{cols2}"
        raise ValueError(msg)

    if rows1 != rows2:
        msg = (
            "Coefficient and constant matrices dimensions must be nxn and nx1 but "
            f"received {rows1}x{cols1} and {rows2}x{cols2}"
        )
        raise ValueError(msg)

    if len(init_val) != rows1:
        msg = (
            "Number of initial values must be equal to number of rows in coefficient "
            f"matrix but received {len(init_val)} and {rows1}"
        )
        raise ValueError(msg)

    if iterations <= 0:
        raise ValueError("Iterations must be at least 1")

    strictly_diagonally_dominant(coefficient_matrix)

    # G5: The function is now agnostic to the float type. It infers the data
    # type from the input matrix for consistency.
    dtype = coefficient_matrix.dtype
    x = np.array(init_val, dtype=dtype)

    # G1, G3: Pre-calculate loop invariants to avoid repeated computation
    # inside the loop.
    D = np.diag(coefficient_matrix)
    b_flat = constant_matrix.flatten()

    # The iteration formula is x_k+1 = D^-1 * (b - R * x_k)
    # We implement this without explicitly creating the matrix R to save memory (G6).
    for _ in range(iterations):
        # G6: Avoid creating the large matrix R. Instead, calculate R @ x as
        # (A @ x - D * x) on the fly. This avoids a large memory allocation.
        off_diag_product = np.dot(coefficient_matrix, x) - D * x
        x = (b_flat - off_diag_product) / D

    # Returning the final values as a list
    return x.tolist()


def strictly_diagonally_dominant(matrix: NDArray[floating]) -> bool:
    """
    Checks if the given matrix is strictly diagonally dominant.
    The condition is: |a_ii| > sum(|a_ij|) for all i where j != i.

    >>> table = np.array([[4, 1, 1], [1, 5, 2], [1, 2, 4]])
    >>> strictly_diagonally_dominant(table)
    True

    >>> table = np.array([[4, 1, 1], [1, 5, 2], [3, 2, 4]])
    >>> strictly_diagonally_dominant(table)
    Traceback (most recent call last):
        ...
    ValueError: Coefficient matrix is not strictly diagonally dominant
    """
    # G1: Compute the absolute value of the matrix once and reuse it.
    abs_matrix = np.abs(matrix)
    # Get the diagonal elements from the absolute matrix
    diag = np.diag(abs_matrix)
    # Sum the absolute values of the off-diagonal elements for each row
    off_diag_sum = np.sum(abs_matrix, axis=1) - diag

    if not np.all(diag > off_diag_sum):
        raise ValueError("Coefficient matrix is not strictly diagonally dominant")

    return True


def generate_sdd_matrix(
    n: int,
) -> tuple[NDArray[floating], NDArray[floating], list[float]]:
    """
    Generates a strictly diagonally dominant (SDD) matrix `A`, a constant vector `b`,
    and an initial guess vector `x0`.
    """
    print(f"Generating a {n}x{n} strictly diagonally dominant matrix...")

    # G5: Use float32 for faster computation and lower memory usage.
    dtype = float32
    A = np.random.rand(n, n).astype(dtype)

    # G1: Compute the absolute value of A once and reuse it.
    abs_A = np.abs(A)
    # Calculate sum of absolute values of off-diagonals for each row
    row_sums = np.sum(abs_A, axis=1) - np.diag(abs_A)

    # Set diagonal elements to be larger than the sum to ensure dominance
    np.fill_diagonal(A, row_sums + np.random.uniform(0.1, 1.0, n).astype(dtype))

    # Generate a random constant matrix b with the same data type
    b = np.random.rand(n, 1).astype(dtype)

    # Generate initial guess x0 (all zeros)
    # G6: This is already efficient, creating a simple list.
    x0 = [0.0] * n

    return A, b, x0


def main(size: str) -> None:
    """
    Main function to run the Jacobi Iteration Method based on problem size.
    """
    print(f"Selected preset: '{size}'")

    if size == "small":
        n = 100  # Updated small size
        print(f"Applying 'small' preset: A generated {n}x{n} system.")
        coefficient, constant, init_val = generate_sdd_matrix(n)
        iterations = 100

    elif size == "large":
        n = 2000  # Updated large size
        print(f"Applying 'large' preset: A generated {n}x{n} system.")
        coefficient, constant, init_val = generate_sdd_matrix(n)
        iterations = 150  # More iterations for a larger system

    else:
        # This case should not be reached due to argparse choices
        print(f"Error: Unknown size '{size}'", file=sys.stderr)
        sys.exit(1)

    print(f"Running Jacobi iteration for {iterations} iterations...")
    start_time = time.time()

    solution = jacobi_iteration_method(coefficient, constant, init_val, iterations)

    end_time = time.time()

    print(f"\nCalculation finished in {end_time - start_time:.4f} seconds.")

    if size == "small":
        print(f"Solution (first 5 elements): {solution[:5]}")
    else:
        # For large solutions, just show a snippet
        print("Solution (first 5 and last 5 elements):")
        print(f"{solution[:5]}...{solution[-5:]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Jacobi Iteration Method for different problem sizes to test performance.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--size",
        choices=["small", "large"],
        required=True,
        help=(
            "Select a problem size:\n"
            "'small': Generates and solves a 100x100 system.\n"
            "'large': Generates and solves a large (2000x2000) strictly\n"
            "         diagonally dominant system."
        ),
    )

    args = parser.parse_args()
    main(args.size)
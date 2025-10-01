"""
Lower-upper (LU) decomposition factors a matrix as a product of a lower
triangular matrix and an upper triangular matrix. A square matrix has an LU
decomposition under the following conditions:

    - If the matrix is invertible, then it has an LU decomposition if and only
      if all of its leading principal minors are non-zero (see
      https://en.wikipedia.org/wiki/Minor_(linear_algebra) for an explanation of
      leading principal minors of a matrix).
    - If the matrix is singular (i.e., not invertible) and it has a rank of k
      (i.e., it has k linearly independent columns), then it has an LU
      decomposition if its first k leading principal minors are non-zero.

This algorithm will simply attempt to perform LU decomposition on any square
matrix and raise an error if no such decomposition exists.

Reference: https://en.wikipedia.org/wiki/LU_decomposition
"""

from __future__ import annotations

import argparse
import sys
import numpy as np


def lower_upper_decomposition(table: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform LU decomposition on a given matrix and raises an error if the matrix
    isn't square or if no such decomposition exists

    >>> matrix = np.array([[2, -2, 1], [0, 1, 2], [5, 3, 1]])
    >>> lower_mat, upper_mat = lower_upper_decomposition(matrix)
    >>> lower_mat
    array([[1. , 0. , 0. ],
           [0. , 1. , 0. ],
           [2.5, 8. , 1. ]])
    >>> upper_mat
    array([[  2. ,  -2. ,   1. ],
           [  0. ,   1. ,   2. ],
           [  0. ,   0. , -17.5]])

    >>> matrix = np.array([[4, 3], [6, 3]])
    >>> lower_mat, upper_mat = lower_upper_decomposition(matrix)
    >>> lower_mat
    array([[1. , 0. ],
           [1.5, 1. ]])
    >>> upper_mat
    array([[ 4. ,  3. ],
           [ 0. , -1.5]])

    >>> # Matrix is not square
    >>> matrix = np.array([[2, -2, 1], [0, 1, 2]])
    >>> lower_mat, upper_mat = lower_upper_decomposition(matrix)
    Traceback (most recent call last):
        ...
    ValueError: 'table' has to be of square shaped array but got a 2x3 array:
    [[ 2 -2  1]
     [ 0  1  2]]

    >>> # Matrix is invertible, but its first leading principal minor is 0
    >>> matrix = np.array([[0, 1], [1, 0]])
    >>> lower_mat, upper_mat = lower_upper_decomposition(matrix)
    Traceback (most recent call last):
    ...
    ArithmeticError: No LU decomposition exists

    >>> # Matrix is singular, but its first leading principal minor is 1
    >>> matrix = np.array([[1, 0], [1, 0]])
    >>> lower_mat, upper_mat = lower_upper_decomposition(matrix)
    >>> lower_mat
    array([[1., 0.],
           [1., 1.]])
    >>> upper_mat
    array([[1., 0.],
           [0., 0.]])

    >>> # Matrix is singular, but its first leading principal minor is 0
    >>> matrix = np.array([[0, 1], [0, 1]])
    >>> lower_mat, upper_mat = lower_upper_decomposition(matrix)
    Traceback (most recent call last):
    ...
    ArithmeticError: No LU decomposition exists
    """
    # Ensure that table is a square array
    rows, columns = np.shape(table)
    if rows != columns:
        msg = (
            "'table' has to be of square shaped array but got a "
            f"{rows}x{columns} array:\n{table}"
        )
        raise ValueError(msg)

    lower = np.zeros((rows, columns))
    upper = np.zeros((rows, columns))

    for i in range(columns):
        # Calculate the i-th row of L (lower triangular matrix)
        # This part is a forward substitution and is inherently sequential.
        for j in range(i):
            dot_product = np.dot(lower[i, :j], upper[:j, j])
            if upper[j, j] == 0:
                raise ArithmeticError("No LU decomposition exists")
            lower[i, j] = (table[i, j] - dot_product) / upper[j, j]

        # The diagonal of L is 1 for Doolittle decomposition
        lower[i, i] = 1

        # G7 Optimization: The calculation for the i-th row of U is vectorized.
        # Instead of a Python loop calculating each element one by one, we use a single
        # bulk matrix-vector multiplication (`np.dot`) to compute the entire row segment.
        # This reduces Python interpreter overhead and leverages NumPy's highly
        # optimized C/Fortran backend for a significant performance increase.
        dot_product_row = np.dot(lower[i, :i], upper[:i, i:])
        upper[i, i:] = table[i, i:] - dot_product_row

    return lower, upper


def main(size_preset: str) -> None:
    """
    Generates a matrix of a given size preset and performs LU decomposition.

    Args:
        size_preset: A string, either "small" or "large", determining the
                     size of the matrix to generate.
    """
    print(f"Selected preset: '{size_preset}'")

    matrix_dim = 0
    if size_preset == "small":
        matrix_dim = 100
        print(f"Generating a 'small' {matrix_dim}x{matrix_dim} random matrix.")
    elif size_preset == "large":
        matrix_dim = 2000
        print(f"Generating a 'large' {matrix_dim}x{matrix_dim} random matrix.")

    # Generate a random square matrix.
    # Using a random matrix makes it highly likely that an LU decomposition exists.
    np.random.seed(42)  # for reproducibility
    matrix = np.random.rand(matrix_dim, matrix_dim)

    print("Performing LU decomposition...")
    try:
        lower_mat, upper_mat = lower_upper_decomposition(matrix)
        print("LU decomposition completed successfully.")
        # We don't print the resulting matrices as they can be very large.
    except (ValueError, ArithmeticError) as e:
        print(f"An error occurred during decomposition: {e}", file=sys.stderr)


if __name__ == "__main__":
    # If the script is run without arguments, run the embedded doctests.
    if len(sys.argv) == 1:
        import doctest
        doctest.testmod()
        print("Doctests passed.")
    else:
        parser = argparse.ArgumentParser(
            description="Perform LU decomposition on a randomly generated square matrix.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser.add_argument(
            "--size",
            choices=["small", "large"],
            required=True,
            help=(
                "Select a data size preset for the matrix:\n"
                "'small': Creates and decomposes a 100x100 matrix.\n"
                "'large': Creates and decomposes a 2000x2000 matrix."
            ),
        )

        args = parser.parse_args()
        main(args.size)
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from math import gcd as greatest_common_divisor


def diophantine(a: int, b: int, c: int) -> tuple[int, int]:
    """
    Solves for a particular integer solution (x, y) to the linear Diophantine equation:
    a*x + b*y = c

    A solution exists if and only if gcd(a, b) divides c.

    GCD (Greatest Common Divisor) or HCF (Highest Common Factor)

    >>> diophantine(10, 6, 14)
    (-7, 14)

    >>> diophantine(391, 299, -69)
    (9, -12)

    Note: The initial particular solution depends on the result of the
    Extended Euclidean Algorithm.
    """
    # G1: The greatest common divisor `d` is computed as part of extended_gcd.
    # We call extended_gcd once and reuse `d` for the solvability check,
    # avoiding a separate, redundant call to greatest_common_divisor(a, b).
    (d, x, y) = extended_gcd(a, b)
    
    assert (
        c % d == 0
    ), "No integer solution exists."
    
    # a*x + b*y = d
    # To get c, we multiply the entire equation by c/d
    # a*(x*c/d) + b*(y*c/d) = c
    r = c // d
    return (r * x, r * y)


def diophantine_all_soln(a: int, b: int, c: int, n: int = 2) -> None:
    """
    Finds and prints 'n' general solutions for the Diophantine equation a*x + b*y = c.

    Theorem: Let gcd(a,b) = d. If (x0, y0) is a particular solution, then
    all solutions are given by:
    x = x0 + t * (b/d)
    y = y0 - t * (a/d)
    where t is an arbitrary integer.

    This function prints 'n' solutions for t = 0, 1, 2, ..., n-1.

    Args:
        a: Coefficient of x.
        b: Coefficient of y.
        c: Constant term.
        n: The number of solutions to generate and print. Defaults to 2.

    >>> diophantine_all_soln(10, 6, 14)
    -7 14
    -4 9

    >>> diophantine_all_soln(10, 6, 14, 4)
    -7 14
    -4 9
    -1 4
    2 -1

    >>> diophantine_all_soln(391, 299, -69, n = 4)
    9 -12
    22 -29
    35 -46
    48 -63
    """
    try:
        # G1: The results of extended_gcd (d, x, y) are needed for both the
        # particular solution and the general solution. We call it once,
        # store the results, and reuse them. This avoids making separate calls
        # to diophantine() and greatest_common_divisor() which would each
        # compute the gcd, resulting in redundant work.
        (d, x_egcd, y_egcd) = extended_gcd(a, b)

        if c % d != 0:
            raise AssertionError("No integer solution exists.")

        # Calculate the initial particular solution (x0, y0)
        # This logic was previously in the separate diophantine() call.
        r = c // d
        x0 = r * x_egcd
        y0 = r * y_egcd
        
        # From the theorem, the offsets for x and y are (b/d) and (a/d)
        q = b // d  # Offset for x
        p = a // d  # Offset for y

        for i in range(n):
            x = x0 + i * q
            y = y0 - i * p
            print(x, y)
            
    except AssertionError as e:
        print(e, file=sys.stderr)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Implements the Extended Euclidean Algorithm.
    Given integers a and b, it finds integers x and y such that a*x + b*y = gcd(a,b).

    Returns:
        A tuple (d, x, y) where d = gcd(a, b).

    >>> extended_gcd(10, 6)
    (2, -1, 2)

    >>> extended_gcd(7, 5)
    (1, -2, 3)
    """
    # This implementation assumes non-negative inputs
    assert a >= 0 and b >= 0

    if b == 0:
        d, x, y = a, 1, 0
    else:
        # G1: Use divmod to compute the quotient (a // b) and remainder (a % b)
        # in a single operation. The results are stored in variables and reused,
        # avoiding a second division operation.
        quotient, remainder = divmod(a, b)
        (d, p, q) = extended_gcd(b, remainder)
        x = q
        y = p - q * quotient

    # Sanity checks to ensure the result is correct
    assert a % d == 0
    assert b % d == 0
    assert d == a * x + b * y

    return (d, x, y)


def main(size: str) -> None:
    """
    Runs the Diophantine equation solver with different scales of data.

    Args:
        size: The data scale, either 'small' or 'large'.
    """
    print(f"Running with preset size: '{size}'")

    if size == "small":
        print("Solving a single equation with moderately sized integers.")
        a, b, c = 391, 299, -69
        n = 10  # Find the first 10 solutions
        print(f"Equation: {a}*x + {b}*y = {c}")
        print(f"Finding {n} solutions:")
        diophantine_all_soln(a, b, c, n)

    elif size == "large":
        print("Solving a single equation with large integers and finding many solutions.")
        # Using 50-digit numbers for a and b to test performance
        a = 15485863123456789012345678901234567890123456789012
        b = 11111111111111111111111111111111111111111111111111
        
        # To ensure a solution exists, c must be a multiple of gcd(a, b).
        # We construct such a c using a large multiplier.
        d = greatest_common_divisor(a, b)
        c = d * 1234567890987654321
        
        n = 10000  # Find many solutions to stress the loop
        
        print(f"Equation involves 50-digit numbers for a and b.")
        print(f"Finding {n} solutions:")
        diophantine_all_soln(a, b, c, n)

    print("\nProcessing complete.")


if __name__ == "__main__":
    # The doctests are kept in the function docstrings and can be run with:
    # python -m doctest your_script_name.py
    #
    # The main part of the script is for performance testing via command-line args.
    
    parser = argparse.ArgumentParser(
        description="Solve Diophantine equations with different data scales for performance testing.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--size",
        choices=["small", "large"],
        required=True,
        help=(
            "Select a data size preset:\n"
            "'small': Solves one equation with moderate-sized integers and finds 10 solutions.\n"
            "'large': Solves one equation with very large (50-digit) integers and finds 10,000 solutions."
        )
    )
    
    args = parser.parse_args()
    main(args.size)
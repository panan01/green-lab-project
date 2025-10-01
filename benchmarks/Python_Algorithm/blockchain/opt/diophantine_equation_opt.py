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
    """
    # G1/G6 Optimization: Call extended_gcd once to get both the GCD (d) and
    # the coefficients. This avoids a separate, redundant call to greatest_common_divisor.
    (d, x, y) = extended_gcd(a, b)
    
    # G6: Reuse 'd' (which is the result of gcd(a,b)) for the existence check.
    assert c % d == 0, "No integer solution exists."
    
    # G1: The common expression c // d is calculated once and stored in a variable 'r'.
    r = c // d
    return (r * x, r * y)


def diophantine_all_soln(a: int, b: int, c: int, n: int = 2) -> None:
    """
    Finds and prints 'n' general solutions for the Diophantine equation a*x + b*y = c.
    This version is fully optimized by applying G1, G6, and G9 methods.
    """
    # G9: The logic from the `diophantine` function is inlined here to reduce function call overhead.
    # G1/G6: Call extended_gcd only ONCE. Its results (d, x_part, y_part) are
    # stored and reused for all subsequent steps (existence check, particular solution,
    # and general solution), avoiding any re-computation of the GCD.
    (d, x_part, y_part) = extended_gcd(a, b)

    # A solution exists if and only if d (which is gcd(a, b)) divides c.
    if c % d != 0:
        print("No integer solution exists.", file=sys.stderr)
        return

    # G1: Store the result of the common expression c // d in a variable 'r' to find
    # the particular solution (x0, y0).
    r = c // d
    x0 = r * x_part
    y0 = r * y_part

    # G6: Reuse 'd' to find the general solution offsets, avoiding another call to gcd().
    q = b // d  # Offset for x
    p = a // d  # Offset for y

    # Loop to generate and print 'n' solutions.
    for i in range(n):
        x = x0 + i * q
        y = y0 - i * p
        print(x, y)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Implements the Extended Euclidean Algorithm.
    Given integers a and b, it finds integers x and y such that a*x + b*y = gcd(a,b).
    """
    assert a >= 0 and b >= 0

    if b == 0:
        d, x, y = a, 1, 0
    else:
        (d, p, q) = extended_gcd(b, a % b)
        x = q
        y = p - q * (a // b)

    assert a % d == 0
    assert b % d == 0
    assert d == a * x + b * y

    return (d, x, y)


def main(size: str) -> None:
    """
    Runs the Diophantine equation solver with different scales of data.
    """
    print(f"Running with preset size: '{size}'")

    if size == "small":
        print("Solving a single equation with moderately sized integers.")
        a, b, c = 391, 299, -69
        n = 10
        print(f"Equation: {a}*x + {b}*y = {c}")
        print(f"Finding {n} solutions:")
        diophantine_all_soln(a, b, c, n)

    elif size == "large":
        print("Solving a single equation with large integers and finding many solutions.")
        a = 15485863123456789012345678901234567890123456789012
        b = 11111111111111111111111111111111111111111111111111
        
        d = greatest_common_divisor(a, b)
        c = d * 1234567890987654321
        
        n = 10000
        
        print(f"Equation involves 50-digit numbers for a and b.")
        print(f"Finding {n} solutions:")
        diophantine_all_soln(a, b, c, n)

    print("\nProcessing complete.")


if __name__ == "__main__":
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
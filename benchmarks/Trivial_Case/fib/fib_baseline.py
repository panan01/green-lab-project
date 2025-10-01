# Violates G18: naive recursion without memoisation
import argparse

def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

def main(size):
    n = 20 if size == "small" else 30
    result = fib(n)
    assert isinstance(result, int)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
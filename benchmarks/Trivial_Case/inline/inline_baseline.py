# Violates G19: uses helper function inside loop repeatedly
import argparse

def square(x):
    return x * x

def main(size):
    N = 10000 if size == "small" else 100000
    total = 0
    for i in range(N):
        total += square(i)
    assert total > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
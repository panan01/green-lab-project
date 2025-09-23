# Applies G19: inline trivial helper function
import argparse

def main(size):
    N = 10000 if size == "small" else 100000
    total = 0
    for i in range(N):
        total += i * i  # inlined
    assert total > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
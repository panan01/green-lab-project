# Violates G6: creates unused intermediate lists
import argparse

def main(size):
    N = 1000 if size == "small" else 100000
    squares = [i*i for i in range(N)]  # unnecessary storage
    total = sum(squares)
    assert total > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
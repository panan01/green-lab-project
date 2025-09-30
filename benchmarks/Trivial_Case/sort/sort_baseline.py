# Violates G2: sorts an already sorted list unnecessarily
import argparse

def main(size):
    N = 1000 if size == "small" else 50000
    data = list(range(N))  # already sorted
    result = sorted(data)  # unnecessary sort
    assert result[0] == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
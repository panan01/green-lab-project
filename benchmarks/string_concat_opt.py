# Applies G7: use ''.join() with list comprehension
import argparse

def main(size):
    N = 1000 if size == "small" else 20000
    s = "".join([str(i) for i in range(N)])  # G7 bulk op
    assert len(s) > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
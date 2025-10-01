# Applies G5: uses x**0.5 instead of math.sqrt for speed
import argparse

def main(size):
    N = 1000 if size == "small" else 50000
    results = [i ** 0.5 for i in range(1, N)]  # approximate computation
    assert len(results) > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
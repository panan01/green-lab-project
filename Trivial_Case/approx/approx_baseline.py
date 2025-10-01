# Violates G5: uses math.sqrt which may be slower than approximation
import argparse, math

def main(size):
    N = 1000 if size == "small" else 50000
    results = [math.sqrt(i) for i in range(1, N)]
    assert len(results) > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
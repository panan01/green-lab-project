# Violates G7: uses string += in loop (inefficient)
import argparse

def main(size):
    N = 1000 if size == "small" else 20000
    s = ""
    for i in range(N):
        s += str(i)
    assert len(s) > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
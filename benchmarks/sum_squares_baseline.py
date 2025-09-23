# Violates G1 and G3: uses repeated global lookups and explicit loop sum
import argparse

def main(size):
    N = 10000 if size == "small" else 500000
    total = 0
    for i in range(N):
        total += i * i
    assert total > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
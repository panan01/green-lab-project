# Applies G1 and G3: local binding + built-in sum with generator
import argparse

def main(size):
    N = 10000 if size == "small" else 500000
    rng = range  # local binding (G1)
    total = sum(i * i for i in rng(N))  # built-in + generator (G3)
    assert total > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
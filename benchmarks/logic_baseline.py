# Violates G4: evaluates both conditions even when short-circuit is possible
import argparse

def check1(x): return x < 10000
def check2(x): return sum(i*i for i in range(x)) > 0

def main(size):
    N = 100 if size == "small" else 10000
    flag = False
    for i in range(N):
        if check1(i) & check2(i):  # & instead of short-circuit
            flag = True
    assert isinstance(flag, bool)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
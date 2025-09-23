# Applies G4: uses short-circuiting with 'and'
import argparse

def check1(x): return x < 10000
def check2(x): return sum(i*i for i in range(x)) > 0

def main(size):
    N = 100 if size == "small" else 10000
    flag = False
    for i in range(N):
        if check1(i) and check2(i):  # short-circuit
            flag = True
    assert isinstance(flag, bool)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large"], required=True)
    args = parser.parse_args()
    main(args.size)
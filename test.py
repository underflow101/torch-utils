import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--a', type=int, default=1)
parser.add_argument('--b', type=int, default=1)
parser.add_argument('--c', type=int, default=1)

config = parser.parse_args()
print(config)
print(config[1])

args = vars(config)
print(args)
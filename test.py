import math

def bucket(value, min_val=-20, max_val=20, num_buckets=10):
    value = max(min_val, min(max_val, value))
    ratio = (value - min_val) / (max_val - min_val)
    return min(int(ratio * num_buckets), num_buckets - 1)


tests = [
    -55,
    55,
    -10,
    10
]
for value in tests:
    x = bucket(value)
    print(x)

"""Print the Min and Max values of each of the keys in the JSON data."""

filepath = r"agent_runs\agent_2026-04-02_12-34-42.json"

import json
import ast

def min_max_values_from_keys(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    min_vals = [None, None, None]
    max_vals = [None, None, None]

    for key in data:
        coords = ast.literal_eval(key)
        for i, val in enumerate(coords):
            if min_vals[i] is None or val < min_vals[i]:
                min_vals[i] = val
            if max_vals[i] is None or val > max_vals[i]:
                max_vals[i] = val

    return min_vals, max_vals

if __name__ == "__main__":
    min_vals, max_vals = min_max_values_from_keys(filepath)
    labels = ['x', 'y', 'z']
    for i, label in enumerate(labels):
        print(f"{label}: min={min_vals[i]}, max={max_vals[i]}")
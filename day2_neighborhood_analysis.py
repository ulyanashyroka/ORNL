import re
from collections import defaultdict
import pandas as pd

file_path = "/Users/ulyana/Desktop/project/ACTIVSg70k/case_ACTIVSg70k.m"
cont_name = "ACTIVSg70k"
max_depth = 5

with open(file_path, "r") as f:
    matpower_text = f.read()

# for mpc.branch section
branch_match = re.search(
    r"mpc\.branch\s*=\s*\[(.*?)\];",
    matpower_text,
    re.DOTALL
)

if not branch_match:
    raise ValueError("Could not find mpc.branch section")

branch_block = branch_match.group(1)


bus_connections = defaultdict(set)

for line in branch_block.split("\n"):
    line = line.strip()
    if not line:
        continue
    if line.startswith("%"):
        continue

    line = line.replace(";", "")
    values = line.split()

    if len(values) < 2:
        continue

    from_bus = int(float(values[0]))
    to_bus = int(float(values[1]))

    bus_connections[from_bus].add(to_bus)
    bus_connections[to_bus].add(from_bus)


def find_bus_neighbors(cont_name, source_bus, max_depth):

    visited_buses = {source_bus}
    current_level_buses = {source_bus}

    results = []

    for depth in range(1, max_depth + 1):

        next_level_buses = set()

        for bus in current_level_buses:
            next_level_buses.update(
                bus_connections.get(bus, set())
            )

        # if the bus is visited, we don't want to count it again
        next_level_buses -= visited_buses

        results.append({
            "cont_name": cont_name,
            "cont_bus": source_bus,
            "neighbor_level": depth,
            "neighb_t": f"N-{depth}",
            "neighbor_count": len(next_level_buses),
            "neighbor_list": sorted(next_level_buses)
        })

        visited_buses.update(next_level_buses)
        current_level_buses = next_level_buses

        if not current_level_buses:
            break

    return results

all_results = []

for source_bus in sorted(bus_connections.keys()):

    neighbor_rows = find_bus_neighbors(
        cont_name,
        source_bus,
        max_depth=max_depth
    )

    all_results.extend(neighbor_rows)

for row in all_results:
    row["neighbor_list"] = ", ".join(
        map(str, row["neighbor_list"])
    )
df = pd.DataFrame(all_results)


pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 200)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", None)
print(df.to_string(index=False))

print(len(df))

print(f"Total rows: {len(df)}")

max_degree_bus = max(
    bus_connections,
    key=lambda b: len(bus_connections[b])
)

print(
    "Highest degree bus:",
    max_degree_bus
)
print(
    "Connections:",
    len(bus_connections[max_degree_bus])
)

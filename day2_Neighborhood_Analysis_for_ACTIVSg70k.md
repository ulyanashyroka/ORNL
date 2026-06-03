# Graph-Based Neighborhood Analysis for ACTIVSg70k

## Goal
The goal of this stage is to construct a graph representation of the ACTIVSg70k transmission network and identify multi-level neighborhoods around each bus.

## Data Source
The network topology is extracted from the MATPOWER case file `case_ACTIVSg70k.m`. Specifically, the analysis uses the `mpc.branch` section, which contains transmission line connections between buses.

```matlab
mpc.branch = [
    fbus  tbus  r  x  ...
];
```

Only the first two columns are required:

- `fbus` = source bus
- `tbus` = destination bus

Each branch is treated as an undirected edge in the network graph.

## Graph Construction

The transmission network is represented as an undirected graph:

- **Vertices** = buses
- **Edges** = transmission lines (`from_bus` → `to_bus`)

The adjacency structure stores:

```python
bus_connections[from_bus].add(to_bus)
bus_connections[to_bus].add(from_bus)
```

This allows rapid neighbor lookup during traversal.

## Neighborhood Discovery

A breadth-first search (BFS) style traversal is used to identify buses located at increasing topological distances from a source bus.

For each source bus:

| Level | Description |
| ----- | ----------- |
| N-1 | Directly connected buses |
| N-2 | Buses reachable in exactly two graph hops |
| N-3 | Buses reachable in exactly three graph hops |
| N-k | Buses reachable in exactly k graph hops |

Previously visited buses are removed at every level to ensure that each bus belongs to only one neighborhood level.

## Output Structure

For every bus in the network, the following information is generated:

| Column | Description |
| -------------- | ------------------------------------ |
| `cont_name` | File name |
| `cont_bus` | Source bus |
| `neighb_t` | Neighborhood level (n-1, n-2, ...) |
| `neighbor_count` | Number of buses at that level |
| `neighbor_list` | List of buses the source connects to |

**Illustration:**

| cont_name | cont_bus | neighb_t | neighbor_count | neighbor_list |
| ----------- | -------- | -------- | -------------- | ------------- |
| ACTIVSg70k | 850 | n-1 | 2 | [857, 858] |

## Future Work

The neighborhood information generated in this stage will be combined with ACOPF simulation results.

For each generator retirement scenario:

1. Obtain post-retirement voltage magnitude (Vm) and voltage angle (Va).
2. Compute delta values:

$$\Delta V_m = V_{m,\text{new}} - V_{m,\text{base}}$$

$$\Delta V_a = V_{a,\text{new}} - V_{a,\text{base}}$$

3. Group buses according to neighborhood level (N-1, N-2, N-3, ...).
4. Compute statistical metrics for each level:
   - Mean ΔVm, Median ΔVm, Min ΔVm, Max ΔVm
   - Mean ΔVa, Median ΔVa, Min ΔVa, Max ΔVa
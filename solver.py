def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])  # Path compression
    return parent[x]

def union(parent, rank, x, y):
    root_x = find(parent, x)
    root_y = find(parent, y)
    if root_x != root_y:
        if rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        elif rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        else:
            parent[root_y] = root_x
            rank[root_x] += 1

# 2. Generate MST (Kruskal's Algorithm)
def generate_mst(data):
    edges = [
        (row["cost"], row["latency"], row["city1"], row["city2"])
        for _, row in data.iterrows()
        if row["cost"] > 0 and row["latency"] > 0
    ]
    
    edges.sort()  # Sort by cost
    
    cities = set(data["city1"]).union(set(data["city2"]))
    parent = {city: city for city in cities}
    rank = {city: 0 for city in cities}

    mst = []
    for cost, latency, city1, city2 in edges:
        if find(parent, city1) != find(parent, city2):
            union(parent, rank, city1, city2)
            mst.append((city1, city2))

    return mst

# 3. Additional Edge Selection (Optional)
def add_additional_edges(data, mst):
    mst_set = set(mst)
    additional_edges = []

    for _, row in data.iterrows():
        edge = (row["city1"], row["city2"])
        if edge not in mst_set and edge[::-1] not in mst_set:
            # Add edges with high latency-to-cost ratio
            ratio = (row["messages"] * max(0, 10_000 - row["latency"])) / row["cost"] if row["cost"] > 0 else 0
            if ratio > 1:  # Threshold to ensure cost-effectiveness
                additional_edges.append(edge)

    return additional_edges
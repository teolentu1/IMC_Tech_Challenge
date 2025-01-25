import os
import pandas as pd
import heapq

DATA_DIR = "data"
SUBMISSIONS_DIR = "submissions"

assert os.path.isdir(DATA_DIR)
assert os.path.isdir(SUBMISSIONS_DIR)

DATA_SET_NAME = "dataset.tsv"

data_set = pd.read_csv(f"{DATA_DIR}/{DATA_SET_NAME}", delimiter="\t", names=["city1", "city2", "latency", "cost", "messages"])


def calculate_profit(latency, messages, max_latency=10000):
    """
    Calculate profit for a given latency and number of messages.
    """
    return max(0, max_latency - latency) * messages


def optimize_connections(data_set):
    """
    Optimize connections to maximize profit while minimizing costs.
    """
    # Extract unique cities
    cities = set(data_set["city1"]) | set(data_set["city2"])
    city_to_index = {city: i for i, city in enumerate(cities)}

    # Create a priority queue for edges with profit-to-cost ratio
    edges = []
    for _, row in data_set.iterrows():
        if row["latency"] > 0 and row["cost"] > 0:
            profit = calculate_profit(row["latency"], row["messages"])
            heapq.heappush(edges, (-profit / row["cost"], profit, row["cost"], row["city1"], row["city2"]))

    # Kruskal's algorithm setup
    parent = {city: city for city in cities}

    def find(city):
        if parent[city] != city:
            parent[city] = find(parent[city])
        return parent[city]

    def union(city1, city2):
        root1 = find(city1)
        root2 = find(city2)
        if root1 != root2:
            parent[root2] = root1

    # Select edges to lease
    leased_edges = set()
    total_cost = 0

    while edges:
        _, profit, cost, city1, city2 = heapq.heappop(edges)
        if find(city1) != find(city2):
            leased_edges.add((city1, city2))
            union(city1, city2)
            total_cost += cost

    return leased_edges, total_cost


def score_submission(submission: set[tuple[str, str]]) -> float:
    """
    Calculate the score for the given submission of leased edges.
    """
    cities = set(data_set["city1"]) | set(data_set["city2"])
    city_to_index = {city: i for i, city in enumerate(cities)}
    max_latency = 10_000

    # Initialize distances and messages
    distances = [[float('inf')] * len(cities) for _ in range(len(cities))]
    messages = [[0] * len(cities) for _ in range(len(cities))]

    # Populate distances and messages from data
    for _, row in data_set.iterrows():
        i1 = city_to_index[row["city1"]]
        i2 = city_to_index[row["city2"]]
        if (row["city1"], row["city2"]) in submission or (row["city2"], row["city1"]) in submission:
            distances[i1][i2] = row["latency"]
            distances[i2][i1] = row["latency"]

        messages[i1][i2] = row["messages"]
        messages[i2][i1] = row["messages"]

    # Floyd-Warshall for shortest paths
    for k in range(len(cities)):
        for i in range(len(cities)):
            for j in range(len(cities)):
                distances[i][j] = min(distances[i][j], distances[i][k] + distances[k][j])

    # Calculate total profit
    profit = 0
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                score_per_message = max(0, max_latency - distances[i][j])
                profit += score_per_message * messages[i][j]

    return profit - sum(row["cost"] for _, row in data_set.iterrows() if (row["city1"], row["city2"]) in submission)


# Run the optimized solver
leased_edges, total_cost = optimize_connections(data_set)

# Output the leased edges as a TSV file
submission_file = f"{SUBMISSIONS_DIR}/optimized_submission.tsv"
with open(submission_file, "w") as f:
    f.write("city1\tcity2\n")  # Add header
    for city1, city2 in leased_edges:
        f.write(f"{city1}\t{city2}\n")

print(f"Submission saved to {submission_file}")

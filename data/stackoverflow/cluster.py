import json
from collections import defaultdict
from sknetwork.hierarchy import LouvainHierarchy, cut_straight
from sknetwork.visualization import visualize_dendrogram
from scipy.sparse import csr_matrix

EDGE_WEIGHT_PROP = "weight"
LOUVAIN_RESOLUTION = 5 # higher values lead to more clusters

with open("result/tags.json", "r") as f:
    tags_json = json.load(f)
with open("result/tag-pairs.json", "r") as f:
    tag_pairs_json = json.load(f)

tags = [tag["tag"] for tag in tags_json]
tag_to_index = {tag: index for index, tag in enumerate(tags)}

# Prepare data for sparse matrix
n = len(tags)
row = []
col = []
data = []

# Fill data for sparse matrix
for edge in tag_pairs_json:
    i, j = tag_to_index[edge["tag1"]], tag_to_index[edge["tag2"]]
    weight = edge[EDGE_WEIGHT_PROP]
    row.extend([i, j])
    col.extend([j, i])
    data.extend([weight, weight])

# Create the sparse adjacency matrix
adj_matrix_csr = csr_matrix((data, (row, col)), shape=(n, n))

# Perform the clustering
louvain = LouvainHierarchy(shuffle_nodes=True, random_state=42, resolution=LOUVAIN_RESOLUTION)
dendrogram = louvain.fit_predict(adj_matrix_csr)
cluster_assignments = cut_straight(dendrogram)

# Assign the cluster index to the tags and create cluster to tags mapping
cluster_to_tags = defaultdict(list)
for idx, tag in enumerate(tags_json):
    cluster = int(cluster_assignments[idx])
    tag['cluster'] = cluster
    cluster_to_tags[cluster].append(tag['tag'])

# Save tags with cluster assignments
with open('result/tags.json', 'w') as f:
    json.dump(tags_json, f, indent=2)

# Save cluster to tags mapping
with open('result/cluster-to-tags.json', 'w') as f:
    json.dump(dict(cluster_to_tags), f, indent=2)

image = visualize_dendrogram(dendrogram, names=tags, rotate=True, width=500, height=7000)
with open('result/dendrogram.svg', 'w') as f:
    f.write(image)

print(f"Found {len(set(cluster_assignments))} clusters.")

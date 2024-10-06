import json

with open("./result/tags.json", "r") as f:
    tags = json.load(f)
with open("./result/tag-pairs.json", "r") as f:
    tag_pairs = json.load(f)

def calculate_weight(pair, max_normalized):
    return pair['pairCountNormalized'] / max_normalized

max_normalized = max(pair['pairCountNormalized'] for pair in tag_pairs)

# Add the new weight property and remove all pairs with a weight below the threshold
updated_tag_pairs = []

for pair in tag_pairs:
    weight = calculate_weight(pair, max_normalized)
    pair['weight'] = weight
    updated_tag_pairs.append(pair)

with open('./result/tag-pairs.json', 'w') as file:
    json.dump(updated_tag_pairs, file, indent=2)

// Simple version - processes everything at once
MATCH (target:Package)

// Find source nodes through specified dependency types
MATCH (source)-[r1]->(target)
WHERE type(r1) IN ["PROD_DEPENDENCY", "PEER_DEPENDENCY", "DEV_DEPENDENCY"]

// Find connected nodes from sources
MATCH (source)-[r2]->(connected)
WHERE connected <> target
AND type(r2) IN ["PROD_DEPENDENCY", "PEER_DEPENDENCY", "DEV_DEPENDENCY"]

// Aggregate and filter by minimum threshold
WITH target, connected, count(DISTINCT source) as occurrence_count
WHERE occurrence_count >= 3

// Create CO_OCCURRENCE relationships
CREATE (target)-[r:CO_OCCURRENCE {count: occurrence_count}]->(connected)

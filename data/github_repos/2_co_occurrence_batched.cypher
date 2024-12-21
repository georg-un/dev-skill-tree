// Batched version - processes in chunks
MATCH (n:Package)
WHERE n.co_occurrence_processed IS NULL
WITH n LIMIT 1000

// Mark nodes as being processed
SET n.co_occurrence_processed = true
WITH n

// Find source nodes through specified dependency types
MATCH (source)-[r1]->(n)
WHERE type(r1) IN ["PROD_DEPENDENCY", "PEER_DEPENDENCY", "DEV_DEPENDENCY"]

// Find connected nodes from sources
MATCH (source)-[r2]->(connected)
WHERE connected <> n
AND type(r2) IN ["PROD_DEPENDENCY", "PEER_DEPENDENCY", "DEV_DEPENDENCY"]

// Aggregate and filter by minimum threshold
WITH n as target, connected, count(DISTINCT source) as occurrence_count
WHERE occurrence_count >= 3

// Create CO_OCCURRENCE relationships
CREATE (target)-[r:CO_OCCURRENCE {count: occurrence_count}]->(connected)

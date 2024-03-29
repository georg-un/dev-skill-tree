/*
This SQL script creates a new table TagPairScores that contains the score of all unique tag pairs found in the FilteredPosts table.
It accounts for tag synonyms by replacing any synonym tag with its corresponding primary tag before counting.
The process involves these main steps:
1. Un-nesting tags from the concatenated Tags field in the FilteredPosts table.
2. Resolving synonyms to their primary tags using the TagSynonyms table.
3. Counting occurrences of each unique tag pair across all posts.
4. Normalizing the count values of each tag pair by the sum of their total counts.
*/

-- Create a new table to store the counts of tag pairs
CREATE TABLE TagPairScores AS

-- CTE to split the concatenated tags into individual rows
WITH UnnestedTags AS (
    SELECT
        p.Id AS PostId,
        -- Split tags into individual elements, removing surrounding <>
        unnest(string_to_array(trim(both '<>' from p.Tags), '><')) AS OriginalTag
    FROM
        FilteredPosts p
),

-- CTE to replace synonym tags with their primary tags
     ResolvedTags AS (
         SELECT
             u.PostId,
             -- Use COALESCE to select the primary tag if available; otherwise, keep the original tag
             COALESCE(ts.PrimaryTag, u.OriginalTag) AS Tag
         FROM
             UnnestedTags u
                 LEFT JOIN
             -- Join with TagSynonyms to find synonym mappings
                 TagSynonyms ts ON u.OriginalTag = ts.SynonymTag
     ),

-- CTE to count occurrences of each unique tag pair
     TagPairs AS (
         SELECT
             a.Tag AS Tag1,
             b.Tag AS Tag2,
             COUNT(*) AS PairCount
         FROM
             ResolvedTags a
                 JOIN
             -- Join ResolvedTags with itself to form pairs, ensuring a.Tag < b.Tag to avoid duplicates
                 ResolvedTags b ON a.PostId = b.PostId AND a.Tag < b.Tag
         GROUP BY
             a.Tag, b.Tag
     ),

-- CTE to retrieve total counts for each tag from the Tags table
     TagCounts AS (
         SELECT
             TagName,
             Count
         FROM
             Tags
     ),

-- CTE to calculate the normalized score for each tag pair
     NormalizedTagPairs AS (
         SELECT
             tp.Tag1,
             tp.Tag2,
             tp.PairCount,
             -- Calculate the normalized score by dividing the pair count by the sum of individual tag counts
             (tp.PairCount::FLOAT / (t1.Count + t2.Count)) AS NormalizedScore
         FROM
             TagPairs tp
                 JOIN
             -- Join with TagCounts to get the count for Tag1
                 TagCounts t1 ON tp.Tag1 = t1.TagName
                 JOIN
             -- Join with TagCounts to get the count for Tag2
                 TagCounts t2 ON tp.Tag2 = t2.TagName
     )

-- Final SELECT to populate the new table with tag pairs and their normalized scores
SELECT
    Tag1,
    Tag2,
    NormalizedScore
FROM
    NormalizedTagPairs
ORDER BY
    NormalizedScore DESC;

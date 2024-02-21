/*
This SQL script creates a new table TagPairCounts that contains the counts of all unique tag pairs found in the FilteredPosts table.
It accounts for tag synonyms by replacing any synonym tag with its corresponding primary tag before counting.
The process involves three main steps:
1. Un-nesting tags from the concatenated Tags field in the FilteredPosts table.
2. Resolving synonyms to their primary tags using the TagSynonyms table.
3. Counting occurrences of each unique tag pair across all posts.
*/

-- Create a new table to store the counts of tag pairs
CREATE TABLE TagPairCounts AS

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
             -- Count the number of posts each pair appears in
             COUNT(*) AS PairCount
         FROM
             ResolvedTags a
                 JOIN
             -- Join ResolvedTags with itself to form pairs, ensuring a.Tag < b.Tag to avoid duplicates
                 ResolvedTags b ON a.PostId = b.PostId AND a.Tag < b.Tag
         GROUP BY
             a.Tag, b.Tag
     )

-- Final SELECT to populate the new table with tag pair counts
SELECT
    Tag1,
    Tag2,
    PairCount
FROM
    TagPairs
ORDER BY
    PairCount DESC;

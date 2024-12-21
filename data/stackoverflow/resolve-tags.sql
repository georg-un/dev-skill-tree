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
     )

SELECT tag, count(*) from ResolvedTags group by tag order by count desc;

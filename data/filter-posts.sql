/*
This SQL script creates the table FilteredPosts containing all rows from the Posts table
where all the following conditions are true:

- PostTypeId is 1 (meaning: post is of type question)
- LastActivityDate is greater equal 01.01.2018
- Score is greater equal -1
- ClosedDate is NULL (meaning: question was not closed)
*/

CREATE TABLE FilteredPosts AS
    SELECT * FROM Posts
             WHERE PostTypeId = 1 AND
                   LastActivityDate >= '2018-01-01' AND
                   Score >= -1 AND
                   ClosedDate IS NULL;

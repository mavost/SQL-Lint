WITH cte AS (
    SELECT id, Name FROM Users u
    JOIN Roles r ON u.roleId = r.id
)
SELECT c.id, r.Name
FROM cte c
JOIN Roles r ON c.id = r.id;


USE SPOT;

GO

WITH [cte] AS (
    SELECT u.[id], r.[Name] FROM [Users] u
    JOIN [Roles] r ON u.[roleId] = r.[id]
)
SELECT c.[id], r.[Name]
FROM [cte] c
JOIN [Roles] r ON c.[id] = r.[id];
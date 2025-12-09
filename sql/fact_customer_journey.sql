
--- CTE to identify and tag duplicate records : Verification Query
-- row_number() : uses -> pagination, remove duplicates, ranking
-- rank() : Rolling SUM - doubt?
WITH DuplicateRecords AS (
	SELECT 
		JourneyID,
		CustomerID,
		ProductID,
		VisitDate,
		Stage,
		Action,
		Duration,
		ROUND(AVG(Duration) OVER (PARTITION BY VisitDate), 2) AS avg_duration,
		ROW_NUMBER() OVER (
			PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action
			ORDER BY JourneyID
		) AS row_num
	FROM
		dbo.customer_journey
)

SELECT JourneyID, CustomerID, ProductID, VisitDate, Stage, Action, COALESCE (Duration, avg_duration) AS Duration
FROM DuplicateRecords
WHERE row_num = 1
ORDER BY JourneyID

-- Outer query : 


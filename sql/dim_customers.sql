

-- Data Enrichment : connect dbo.customers with dbo.geography, for adding geographic information
SELECT
	c.CustomerID,
	c.CustomerName,
	c.Email,
	c.Gender,
	c.Age,
	g.Country,
	g.City
FROM
	dbo.customers as c
LEFT JOIN
	dbo.geography as g
ON
	c.GeographyID = g.GeographyID;
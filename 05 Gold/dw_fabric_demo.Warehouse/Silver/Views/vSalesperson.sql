-- Auto Generated (Do not modify) EFDF54E34C60E073C1640A9FAE4009E4C792014E2398DBEE3FD6128B73C7AC5E


  CREATE       VIEW [Silver].[vSalesperson] AS (SELECT [PersonID], [FullName]        
FROM [lh_fabric_demo].[dbo].[People]
WHERE [IsSalesperson] = 1)
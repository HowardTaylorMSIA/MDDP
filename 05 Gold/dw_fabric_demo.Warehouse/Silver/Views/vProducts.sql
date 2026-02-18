-- Auto Generated (Do not modify) FCB2116614326F19A7740172825510C90F7998EBFA166A030599EB0A7AD9859D



CREATE         VIEW [Silver].[vProducts] AS (SELECT       isnull( [Brand],'No Brand') as Brand
            ,[ColorName]
            ,[LeadTimeDays]
            ,[StockItemID]
            ,[StockItemName]
            ,S.[SupplierID]
            ,[SupplierName]
FROM [lh_fabric_demo].[dbo].[StockItems] P
inner join [lh_fabric_demo].[dbo].[Suppliers] S 
on S.SupplierID = P.SupplierID
inner join [lh_fabric_demo].[dbo].[Colors] C
on P.ColorID = C.ColorID)
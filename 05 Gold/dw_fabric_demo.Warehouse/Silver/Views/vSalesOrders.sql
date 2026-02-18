-- Auto Generated (Do not modify) F517B55D244DA8FDDCBF0AF7644884610BD7CA28FAB4884BA846BA9014D6673F



CREATE       VIEW [Silver].[vSalesOrders] AS (SELECT     
             O.[OrderID]
            ,[OrderLineID]
            ,[CustomerID]
            ,[StockItemID]
            ,[SalespersonPersonID]
            ,[OrderDate]
            ,[Quantity]
            ,[Quantity] * [UnitPrice] as ExtendedPrice
            ,case when  O.[LastEditedWhen] >= L.[LastEditedWhen] then O.LastEditedWhen else L.[LastEditedWhen] end as LastUpdated
FROM [lh_fabric_demo].[dbo].[orders] O
 inner join [lh_fabric_demo].[dbo].[orderlines] L
 on O.OrderID = L.OrderID)
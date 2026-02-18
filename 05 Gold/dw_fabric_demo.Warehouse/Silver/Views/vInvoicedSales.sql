-- Auto Generated (Do not modify) 019964FF296985BE6F278090BDFC8A64BB1A16DB29F0A61C4060A51254BB2C7B


CREATE       VIEW [Silver].[vInvoicedSales] AS (SELECT       I.[InvoiceID]
            ,[InvoiceLineID]
            ,[CustomerID]
            ,[StockItemID]
            ,[SalespersonPersonID]
            ,[InvoiceDate]
            , Case when I.[LastEditedWhen] > L.LastEditedWhen then I.LastEditedWhen else L.LastEditedWhen end as LastUpdated
            ,[Quantity]
            ,[ExtendedPrice]
            ,[LineProfit] as GrossProfit
            ,[TaxAmount]
FROM [lh_fabric_demo].[dbo].[invoices] I 
inner join [lh_fabric_demo].[dbo].[invoicelines] L
on I.InvoiceID = L.InvoiceID)
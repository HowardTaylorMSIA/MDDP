CREATE TABLE [Gold].[SalesOrders] (

	[OrderID] int NOT NULL, 
	[OrderLineID] int NOT NULL, 
	[CustomerID] int NULL, 
	[StockItemID] int NULL, 
	[SalespersonPersonID] int NULL, 
	[OrderDate] date NULL, 
	[Quantity] int NULL, 
	[ExtendedPrice] decimal(18,2) NULL, 
	[LastUpdated] datetime2(6) NULL
);
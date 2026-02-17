CREATE TABLE [Gold].[InvoicedSales] (

	[InvoiceID]           int           NOT NULL,
	[InvoiceLineID]       int           NOT NULL,
	[InvoiceDate]         date          NULL,
	[CustomerID]          int           NULL,
	[StockItemID]         int           NULL,
	[SalespersonPersonID] int           NULL,
	[Quantity]            int           NULL,
	[ExtendedPrice]       decimal(18,2) NULL,
	[GrossProfit]         decimal(18,2) NULL,
	[TaxAmount]           decimal(18,2) NULL,
	[LastUpdated]         datetime2(6)  NULL
);
-- Find/Replace [lh_fabric_demo] with your Warehouse Name
CREATE         PROC [Gold].[IncrLoadInvoicedSales]
@StartDate DATETIME,
@EndDate DATETIME
AS
BEGIN

SET NOCOUNT ON;

DECLARE @UpdateCount INT, @InsertCount INT
-- exec [Gold].[IncrLoadInvoicedSales] null, null 

IF @StartDate IS NULL
BEGIN
    SELECT @StartDate = isnull(MAX(LastUpdated),'2013-01-01') 
    FROM [lh_fabric_demo].[dbo].[InvoicedSales]
END;

IF @EndDate IS NULL
BEGIN
    SET @EndDate = '9999-12-31'
END    

UPDATE target
SET target.InvoiceDate = source.InvoiceDate,
            target.CustomerID = source.CustomerID,
            target.StockItemID = source.StockItemID,
            target.SalespersonPersonID = source.SalespersonPersonID,
            target.ExtendedPrice = source.ExtendedPrice,
            target.Quantity = source.Quantity,
            target.GrossProfit = source.GrossProfit,
            target.TaxAmount = source.TaxAmount,
            target.LastUpdated = source.LastUpdated
FROM [lh_fabric_demo].[dbo].[InvoicedSales] AS target
    INNER JOIN [lh_fabric_demo].[Silver].[vInvoicedSales] AS source
    ON (target.InvoiceID = source.InvoiceID AND target.InvoiceLineID = source.InvoiceLineID)
    WHERE source.LastUpdated BETWEEN @StartDate and @EndDate;

 SELECT @UpdateCount = @@ROWCOUNT   

INSERT INTO [lh_fabric_demo].[dbo].[InvoicedSales] (InvoiceID, InvoiceLineID, InvoiceDate, CustomerID, StockItemID, SalespersonPersonID, 
            ExtendedPrice, Quantity,GrossProfit,TaxAmount, LastUpdated)
    SELECT source.InvoiceID, source.InvoiceLineID, source.InvoiceDate, source.CustomerID, source.StockItemID, source.SalespersonPersonID,
            source.ExtendedPrice, source.Quantity, source.GrossProfit, source.TaxAmount,source.LastUpdated
    FROM [lh_fabric_demo].[Silver].[vInvoicedSales] AS source
    LEFT JOIN [lh_fabric_demo].[dbo].[InvoicedSales] AS target
    ON (target.InvoiceID = source.InvoiceID AND target.InvoiceLineID = source.InvoiceLineID)
    WHERE target.InvoiceID IS NULL AND target.InvoiceLineID IS NULL AND source.LastUpdated  BETWEEN @StartDate and @EndDate
END

 SELECT @InsertCount = @@ROWCOUNT  

 SELECT @UpdateCount as UpdateCount, @InsertCount as InsertCount, @StartDate as MaxDate
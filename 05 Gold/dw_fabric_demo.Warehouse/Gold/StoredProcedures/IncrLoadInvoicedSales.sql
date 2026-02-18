/*
================================================================================
  Procedure : Gold.IncrLoadInvoicedSales
  Purpose   : Incrementally load InvoicedSales from warehouse Silver view to
              warehouse Gold table using UPDATE-then-INSERT pattern.
  Parameters:
      @StartDate DATETIME - Lower bound for LastUpdated filter (inclusive).
                            NULL = auto-detect from MAX(LastUpdated) in target.
      @EndDate   DATETIME - Upper bound for LastUpdated filter (inclusive).
                            NULL = defaults to 9999-12-31 (no upper bound).
  Returns   : Single-row result set with UpdateCount, InsertCount, MaxDate.
  Notes     : Fabric Warehouse does not support MERGE; UPDATE+INSERT is the
              standard incremental pattern on this platform.
================================================================================
*/
CREATE PROC [Gold].[IncrLoadInvoicedSales]
    @StartDate DATETIME,
    @EndDate   DATETIME
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @UpdateCount INT, @InsertCount INT;

    -- Default @StartDate to the current high-watermark in the target table
    IF @StartDate IS NULL
    BEGIN
        SELECT @StartDate = ISNULL(MAX(LastUpdated), '2013-01-01')
        FROM [Gold].[InvoicedSales];
    END;

    -- Default @EndDate to far-future (no upper bound)
    IF @EndDate IS NULL
    BEGIN
        SET @EndDate = '9999-12-31';
    END;

    --------------------------------------------------------------------------
    -- Step 1: UPDATE existing rows that have changed in the source
    --------------------------------------------------------------------------
    UPDATE target
    SET target.InvoiceDate         = source.InvoiceDate,
        target.CustomerID          = source.CustomerID,
        target.StockItemID         = source.StockItemID,
        target.SalespersonPersonID = source.SalespersonPersonID,
        target.ExtendedPrice       = source.ExtendedPrice,
        target.Quantity            = source.Quantity,
        target.GrossProfit         = source.GrossProfit,
        target.TaxAmount           = source.TaxAmount,
        target.LastUpdated         = source.LastUpdated
    FROM [Gold].[InvoicedSales] AS target
    INNER JOIN [Silver].[vInvoicedSales] AS source
        ON  target.InvoiceID     = source.InvoiceID
        AND target.InvoiceLineID = source.InvoiceLineID
    WHERE source.LastUpdated >= @StartDate
      AND source.LastUpdated <= @EndDate;

    SET @UpdateCount = @@ROWCOUNT;

    --------------------------------------------------------------------------
    -- Step 2: INSERT rows that exist in source but not yet in target
    --------------------------------------------------------------------------
    INSERT INTO [Gold].[InvoicedSales]
        (InvoiceID, InvoiceLineID, InvoiceDate, CustomerID, StockItemID,
         SalespersonPersonID, ExtendedPrice, Quantity, GrossProfit,
         TaxAmount, LastUpdated)
    SELECT
        source.InvoiceID,
        source.InvoiceLineID,
        source.InvoiceDate,
        source.CustomerID,
        source.StockItemID,
        source.SalespersonPersonID,
        source.ExtendedPrice,
        source.Quantity,
        source.GrossProfit,
        source.TaxAmount,
        source.LastUpdated
    FROM [Silver].[vInvoicedSales] AS source
    LEFT JOIN [Gold].[InvoicedSales] AS target
        ON  target.InvoiceID     = source.InvoiceID
        AND target.InvoiceLineID = source.InvoiceLineID
    WHERE target.InvoiceID IS NULL
      AND source.LastUpdated >= @StartDate
      AND source.LastUpdated <= @EndDate;

    SET @InsertCount = @@ROWCOUNT;

    --------------------------------------------------------------------------
    -- Step 3: Return execution metrics
    --------------------------------------------------------------------------
    SELECT
        @UpdateCount AS UpdateCount,
        @InsertCount AS InsertCount,
        (SELECT MAX(LastUpdated)
         FROM [Gold].[InvoicedSales]) AS MaxDate;
END;
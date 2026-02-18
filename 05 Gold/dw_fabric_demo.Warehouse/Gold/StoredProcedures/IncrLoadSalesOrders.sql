/*
================================================================================
  Procedure : Gold.IncrLoadSalesOrders
  Purpose   : Incrementally load SalesOrders from lakehouse Silver view to
              warehouse Gold table using UPDATE-then-INSERT pattern.
  Parameters:
      @StartDate DATETIME - Lower bound for LastUpdated filter (inclusive).
                            NULL = auto-detect from MAX(LastUpdated) in target.
      @EndDate   DATETIME - Upper bound for LastUpdated filter (inclusive).
                            NULL = defaults to 9999-12-31 (no upper bound).
  Returns   : Single-row result set with UpdateCount, InsertCount, MaxDate.
================================================================================
*/
CREATE PROC [Gold].[IncrLoadSalesOrders]
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
        FROM [dw_fabric_demo].[Gold].[SalesOrders];
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
    SET target.OrderDate           = source.OrderDate,
        target.CustomerID          = source.CustomerID,
        target.StockItemID         = source.StockItemID,
        target.SalespersonPersonID = source.SalespersonPersonID,
        target.ExtendedPrice       = source.ExtendedPrice,
        target.Quantity            = source.Quantity,
        target.LastUpdated         = source.LastUpdated
    FROM [dw_fabric_demo].[Gold].[SalesOrders] AS target
    INNER JOIN [dw_fabric_demo].[Silver].[vSalesOrders] AS source
        ON  target.OrderID     = source.OrderID
        AND target.OrderLineID = source.OrderLineID
    WHERE source.LastUpdated >= @StartDate
      AND source.LastUpdated <= @EndDate;

    SET @UpdateCount = @@ROWCOUNT;

    --------------------------------------------------------------------------
    -- Step 2: INSERT rows that exist in source but not yet in target
    --------------------------------------------------------------------------
    INSERT INTO [dw_fabric_demo].[Gold].[SalesOrders]
        (OrderID, OrderLineID, OrderDate, CustomerID, StockItemID,
         SalespersonPersonID, ExtendedPrice, Quantity, LastUpdated)
    SELECT
        source.OrderID,
        source.OrderLineID,
        source.OrderDate,
        source.CustomerID,
        source.StockItemID,
        source.SalespersonPersonID,
        source.ExtendedPrice,
        source.Quantity,
        source.LastUpdated
    FROM [dw_fabric_demo].[Silver].[vSalesOrders] AS source
    LEFT JOIN [dw_fabric_demo].[Gold].[SalesOrders] AS target
        ON  target.OrderID     = source.OrderID
        AND target.OrderLineID = source.OrderLineID
    WHERE target.OrderID IS NULL
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
         FROM [dw_fabric_demo].[Gold].[SalesOrders]) AS MaxDate;
END;
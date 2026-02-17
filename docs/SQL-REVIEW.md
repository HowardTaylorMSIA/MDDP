# SQL Review — mddp (Metadata-Driven Data Platform)

**Review Date:** 2026-02-16  
**Scope:** All SQL in the Fabric workspace — `.sql` files, embedded SQL in pipeline JSON, and Spark SQL in notebooks  
**Reviewer:** Automated SQL Architecture Review

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Inventory of SQL Statements](#2-inventory-of-sql-statements)
3. [Schema Definitions (DDL)](#3-schema-definitions-ddl)
4. [Stored Procedures](#4-stored-procedures)
5. [Pipeline Embedded SQL](#5-pipeline-embedded-sql)
6. [Notebook Spark SQL](#6-notebook-spark-sql)
7. [Issues & Anti-Patterns](#7-issues--anti-patterns)
8. [Recommendations](#8-recommendations)
9. [Rewritten SQL](#9-rewritten-sql)
10. [Assumptions](#10-assumptions)

---

## 1. High-Level Overview

The SQL in this project serves a **star-schema data warehouse** pattern implemented on Microsoft Fabric:

```
Source (Azure SQL / WWI)
  │
  ▼
Bronze (Lakehouse Delta tables) ← SELECT queries via Copy Activity
  │
  ▼
Gold (Fabric Warehouse) ← Full-load DELETE+INSERT or Incremental MERGE via stored procedures
  │
  ▼
Metadata (SQL Database) ← UPDATE statements logging pipeline execution status
```

**SQL Categories:**

| Category | Count | Location |
|----------|-------|----------|
| Schema DDL | 1 | `Gold/Gold.sql` |
| Table DDL | 9 | `Gold/Tables/*.sql`, `dbo/Tables/*.sql` |
| Stored Procedures | 2 | `Gold/StoredProcedures/*.sql` |
| Pipeline Lookup queries | 4 | Pipeline JSON (orchestrator, bronze, gold) |
| Pipeline Script activities | 8 | Pipeline JSON (bronze × 4, gold × 4) |
| Pipeline Copy source queries | 3 | Pipeline JSON (bronze × 2, gold × 1) |
| Pipeline pre-copy scripts | 1 | Pipeline JSON (gold DELETE) |
| Notebook Spark SQL | 2 | `SHOW TABLES`, `OPTIMIZE ... VORDER` |

---

## 2. Inventory of SQL Statements

### 2.1 DDL Files (`.sql`)

| File | Type | Object |
|------|------|--------|
| `Gold/Gold.sql` | `CREATE SCHEMA` | `Gold` |
| `Gold/Tables/Calendar.sql` | `CREATE TABLE` | `Gold.Calendar` |
| `Gold/Tables/Customer.sql` | `CREATE TABLE` | `Gold.Customer` |
| `Gold/Tables/InvoicedSales.sql` | `CREATE TABLE` | `Gold.InvoicedSales` |
| `Gold/Tables/Products.sql` | `CREATE TABLE` | `Gold.Products` |
| `Gold/Tables/SalesOrders.sql` | `CREATE TABLE` | `Gold.SalesOrders` |
| `Gold/Tables/Salesperson.sql` | `CREATE TABLE` | `Gold.Salesperson` |
| `dbo/Tables/PipelineOrchestrator_FabricLakehouse.sql` | `CREATE TABLE` | `dbo.PipelineOrchestrator_FabricLakehouse` |
| `dbo/Tables/PipelineOrchestrator_FabricLakehouseGold.sql` | `CREATE TABLE` | `dbo.PipelineOrchestrator_FabricLakehouseGold` |
| `dbo/Tables/PipelineOrchestrator_FabricWarehouse.sql` | `CREATE TABLE` | `dbo.PipelineOrchestrator_FabricWarehouse` |

### 2.2 Stored Procedures

| File | Procedure | Purpose |
|------|-----------|---------|
| `Gold/StoredProcedures/IncrLoadInvoicedSales.sql` | `Gold.IncrLoadInvoicedSales` | Incremental UPDATE+INSERT for InvoicedSales |
| `Gold/StoredProcedures/IncrLoadSalesOrders.sql` | `Gold.IncrLoadSalesOrders` | Incremental UPDATE+INSERT for SalesOrders |

### 2.3 Pipeline Embedded SQL

| Pipeline | Activity | SQL Operation |
|----------|----------|---------------|
| Orchestrator | Get tables to load to deltalake | `SELECT` (metadata lookup) |
| Orchestrator | Get tables to load to warehouse | `SELECT` (metadata lookup) |
| Bronze | Copy data to delta table | `SELECT` (source extraction) |
| Bronze | Copy data to parquet | `SELECT` (source extraction, incremental) |
| Bronze | Update Pipeline Run details (×2) | `UPDATE` (status logging) |
| Bronze | Log Load Failure (×2) | `UPDATE` (failure logging) |
| Gold | Copy data to warehouse | `SELECT` + `DELETE` (full load) |
| Gold | Load Incremental via Stored Proc | `EXEC` stored procedure |
| Gold | Update Pipeline Run details (×2) | `UPDATE` (status logging) |
| Gold | Log Load Failure (×2) | `UPDATE` (failure logging) |

---

## 3. Schema Definitions (DDL)

### 3.1 Gold Schema — Fact Tables

#### `Gold.InvoicedSales`
```sql
CREATE TABLE [Gold].[InvoicedSales] (
    [InvoiceID]           int            NOT NULL,
    [InvoiceLineID]       int            NOT NULL,
    [CustomerID]          int            NULL,
    [StockItemID]         int            NULL,
    [SalespersonPersonID] int            NULL,
    [InvoiceDate]         date           NULL,
    [LastUpdated]         datetime2(6)   NULL,
    [Quantity]            int            NULL,
    [ExtendedPrice]       decimal(18,2)  NULL,
    [GrossProfit]         decimal(18,2)  NULL,
    [TaxAmount]           decimal(18,2)  NULL
);
```

**Analysis:**
- Composite natural key: `(InvoiceID, InvoiceLineID)` — both `NOT NULL`, used as join key in stored procedures
- No PRIMARY KEY constraint defined
- All FK and measure columns allow NULL — FK columns should arguably be NOT NULL
- `LastUpdated` used as the high-watermark for incremental loads

#### `Gold.SalesOrders`
```sql
CREATE TABLE [Gold].[SalesOrders] (
    [OrderID]             int            NOT NULL,
    [OrderLineID]         int            NOT NULL,
    [CustomerID]          int            NULL,
    [StockItemID]         int            NULL,
    [SalespersonPersonID] int            NULL,
    [OrderDate]           date           NULL,
    [Quantity]            int            NULL,
    [ExtendedPrice]       decimal(18,2)  NULL,
    [LastUpdated]         datetime2(6)   NULL
);
```

**Analysis:**
- Same pattern as InvoicedSales — composite natural key, no PK constraint
- Missing `GrossProfit` and `TaxAmount` (expected — orders don't have these until invoiced)

### 3.2 Gold Schema — Dimension Tables

#### `Gold.Customer`
```sql
CREATE TABLE [Gold].[Customer] (
    [YearsCustomer]         int           NULL,
    [BuyingGroupID]         int           NULL,
    [BuyingGroupName]       varchar(50)   NULL,
    [CreditLimit]           decimal(10,2) NULL,
    [CustomerCategoryID]    int           NULL,
    [CustomerID]            int           NOT NULL,
    [CustomerName]          varchar(100)  NULL,
    [DeliveryCityID]        int           NULL,
    [DeliveryCity]          varchar(50)   NULL,
    [DeliveryStateProvince] varchar(50)   NULL,
    [DeliveryCountry]       varchar(60)   NULL,
    [Region]                varchar(30)   NULL,
    [Subregion]             varchar(30)   NULL,
    [Continent]             varchar(30)   NULL,
    [SalesTerritory]        varchar(50)   NULL,
    [DeliveryPostalCode]    varchar(10)   NULL,
    [IsOnCreditHold]        bit           NULL,
    [PaymentDays]           int           NULL,
    [AreaCode]              varchar(3)    NULL
);
```

**Analysis:**
- `CustomerID` is `NOT NULL` but no PK constraint
- Columns are not in a logical order — `YearsCustomer` is first (a derived metric), `CustomerID` (the key) is sixth
- Contains denormalized geographic hierarchy: City → State → Country → Region → Subregion → Continent

#### `Gold.Products`
```sql
CREATE TABLE [Gold].[Products] (
    [StockItemID]   int          NOT NULL,
    [StockItemName] varchar(100) NULL,
    [SupplierID]    int          NULL,
    [SupplierName]  varchar(100) NULL,
    [Brand]         varchar(20)  NULL,
    [ColorName]     varchar(20)  NULL,
    [LeadTimeDays]  int          NULL
);
```

#### `Gold.Salesperson`
```sql
CREATE TABLE [Gold].[Salesperson] (
    [PersonID] int         NOT NULL,
    [FullName] varchar(50) NULL
);
```

#### `Gold.Calendar`
```sql
CREATE TABLE [Gold].[Calendar] (
    [Date]         date        NOT NULL,
    [DayNum]       smallint    NULL,
    [DayOfWeek]    varchar(20) NULL,
    [DayOfWeekNum] smallint    NULL,
    [Month]        varchar(20) NULL,
    [MonthNum]     smallint    NULL,
    [QuarterNum]   smallint    NULL,
    [Quarter]      varchar(2)  NULL,
    [Year]         smallint    NULL
);
```

### 3.3 Metadata Tables

#### `dbo.PipelineOrchestrator_FabricLakehouse`
Drives bronze layer loading — one row per source table.

| Column | Purpose |
|--------|---------|
| `pipelinename` | Child pipeline name |
| `sqlsourceschema`, `sqlsourcetable` | Source table coordinates |
| `sourcecolumns` | Column list for SELECT (allows column exclusion) |
| `sqlsourcedatecolumn` | Watermark column for incremental loads |
| `sourcekeycolumn` | MERGE key column |
| `sqlstartdate`, `sqlenddate` | Date range filter |
| `sinktablename` | Target lakehouse table name |
| `loadtype` | `full` or `incremental` |
| `skipload` | Skip flag |
| `batchloaddatetime` through `pipelineendtime` | Execution audit columns |

#### `dbo.PipelineOrchestrator_FabricLakehouseGold`
Appears to be an intermediate/unused metadata table.

#### `dbo.PipelineOrchestrator_FabricWarehouse`
Drives gold layer loading — one row per warehouse table.

| Column | Purpose |
|--------|---------|
| `storedprocschema`, `storedprocname` | Stored procedure for incremental loads |
| `sinkschema`, `sinktable` | Target warehouse table |
| `rowsupdated`, `rowsinserted` | Execution metrics |

---

## 4. Stored Procedures

### 4.1 `Gold.IncrLoadInvoicedSales`

**Purpose:** Incrementally load InvoicedSales from lakehouse Silver view to warehouse Gold table using an UPDATE-then-INSERT pattern (poor man's MERGE).

**Step-by-step:**

1. **Parameter defaults:** If `@StartDate` is NULL, read `MAX(LastUpdated)` from target (fallback `2013-01-01`). If `@EndDate` is NULL, set to `9999-12-31`.
2. **UPDATE existing rows:** Join target to source on `(InvoiceID, InvoiceLineID)` where source `LastUpdated` is within the date range. Update all non-key columns.
3. **INSERT new rows:** LEFT JOIN source to target on same key; insert where target key IS NULL and source within date range.
4. **Return metrics:** Output `UpdateCount`, `InsertCount`, and current `MaxDate`.

```sql
CREATE PROC [Gold].[IncrLoadInvoicedSales]
    @StartDate DATETIME,
    @EndDate DATETIME
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @UpdateCount INT, @InsertCount INT

    IF @StartDate IS NULL
    BEGIN
        SELECT @StartDate = ISNULL(MAX(LastUpdated), '2013-01-01')
        FROM [dw_fabric_demo].[Gold].[InvoicedSales]
    END;

    IF @EndDate IS NULL
    BEGIN
        SET @EndDate = '9999-12-31'
    END

    -- UPDATE existing rows
    UPDATE target
    SET target.InvoiceDate          = source.InvoiceDate,
        target.CustomerID           = source.CustomerID,
        target.StockItemID          = source.StockItemID,
        target.SalespersonPersonID  = source.SalespersonPersonID,
        target.ExtendedPrice        = source.ExtendedPrice,
        target.Quantity             = source.Quantity,
        target.GrossProfit          = source.GrossProfit,
        target.TaxAmount            = source.TaxAmount,
        target.LastUpdated          = source.LastUpdated
    FROM [dw_fabric_demo].[Gold].[InvoicedSales] AS target
    INNER JOIN [lh_fabric_demo].[Silver].[vInvoicedSales] AS source
        ON target.InvoiceID = source.InvoiceID
        AND target.InvoiceLineID = source.InvoiceLineID
    WHERE source.LastUpdated BETWEEN @StartDate AND @EndDate;

    SELECT @UpdateCount = @@ROWCOUNT;

    -- INSERT new rows
    INSERT INTO [dw_fabric_demo].[Gold].[InvoicedSales]
        (InvoiceID, InvoiceLineID, InvoiceDate, CustomerID, StockItemID,
         SalespersonPersonID, ExtendedPrice, Quantity, GrossProfit, TaxAmount, LastUpdated)
    SELECT source.InvoiceID, source.InvoiceLineID, source.InvoiceDate,
           source.CustomerID, source.StockItemID, source.SalespersonPersonID,
           source.ExtendedPrice, source.Quantity, source.GrossProfit,
           source.TaxAmount, source.LastUpdated
    FROM [lh_fabric_demo].[Silver].[vInvoicedSales] AS source
    LEFT JOIN [dw_fabric_demo].[Gold].[InvoicedSales] AS target
        ON target.InvoiceID = source.InvoiceID
        AND target.InvoiceLineID = source.InvoiceLineID
    WHERE target.InvoiceID IS NULL
      AND target.InvoiceLineID IS NULL
      AND source.LastUpdated BETWEEN @StartDate AND @EndDate;

    SELECT @InsertCount = @@ROWCOUNT;

    SELECT @UpdateCount AS UpdateCount,
           @InsertCount AS InsertCount,
           (SELECT MAX(LastUpdated) FROM [dw_fabric_demo].[Gold].[InvoicedSales]) AS MaxDate;
END
```

### 4.2 `Gold.IncrLoadSalesOrders`

**Purpose:** Same UPDATE-then-INSERT pattern for SalesOrders.

**Identical structure** to `IncrLoadInvoicedSales` but with SalesOrders columns (no `GrossProfit` / `TaxAmount`).

---

## 5. Pipeline Embedded SQL

### 5.1 Orchestrator Lookup Queries

**Get tables to load to deltalake:**
```sql
SELECT * FROM dbo.PipelineOrchestrator_FabricLakehouse
WHERE skipload = 0 AND 1 = @{pipeline().parameters.loadbronze}
```

**Get tables to load to warehouse:**
```sql
SELECT * FROM dbo.PipelineOrchestrator_FabricWarehouse
WHERE skipload = 0 AND @{pipeline().parameters.loaddwh} = 1
```

### 5.2 Bronze Copy Source Queries

```sql
SELECT @{pipeline().parameters.sourcecolumns}
FROM @{pipeline().parameters.sqlsourceschema}.@{pipeline().parameters.sqlsourcetable}
WHERE @{variables('datepredicate')}
```

### 5.3 Gold Copy Source & Pre-Copy

```sql
-- Source
SELECT * FROM @{pipeline().parameters.sourceschema}.@{pipeline().parameters.sourcetable}

-- Pre-copy (truncate replacement)
DELETE FROM @{pipeline().parameters.sinkschema}.@{pipeline().parameters.sinktable}
```

### 5.4 Status Update Scripts (Bronze & Gold)

All follow the same pattern — `UPDATE ... SET audit_columns WHERE key_columns`:

```sql
UPDATE dbo.PipelineOrchestrator_FabricLakehouse
SET batchloaddatetime = '...',
    loadstatus = '...',
    rowsread = ...,
    rowscopied = ...,
    ...
WHERE sqlsourceschema = '...' AND sqlsourcetable = '...'
```

---

## 6. Notebook Spark SQL

### 6.1 Optimize Lakehouse Tables Notebook

```python
spark.sql("SHOW TABLES")                          # Discover all Delta tables
spark.sql(f"OPTIMIZE `{table_name}` VORDER")      # Compact with V-Order encoding
delta_table.vacuum(vacuum_retention_hours)          # Remove old files (DeltaTable API)
```

### 6.2 Create or Merge to Deltalake Notebook

Uses DeltaTable Python API (not raw SQL):
```python
deltaTable.alias("t").merge(
    df2.alias("s"), mergeKeyExpr
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

---

## 7. Issues & Anti-Patterns

### 7.1 CRITICAL — SQL Injection Risk in Pipeline Queries

| Severity | Location | Issue |
|----------|----------|-------|
| **CRITICAL** | Bronze Copy source query | `SELECT @{pipeline().parameters.sourcecolumns} FROM @{...schema}.@{...table}` — column names, schema, and table are injected directly from metadata without quoting. If metadata contained malicious values, arbitrary SQL could execute. |
| **CRITICAL** | Gold Copy source query | `SELECT * FROM @{...schema}.@{...table}` — same injection pattern for schema/table. |
| **CRITICAL** | Gold pre-copy script | `DELETE FROM @{...schema}.@{...table}` — unquoted identifiers. |

**Mitigation:** These values come from a controlled metadata database, not user input. Risk is low in practice but violates defense-in-depth. Add `QUOTENAME()` wrapping where possible, or bracket-quote identifiers in the metadata values themselves.

### 7.2 HIGH — No Primary Key Constraints on Gold Tables

| Severity | Location | Issue |
|----------|----------|-------|
| **HIGH** | All Gold tables | No `PRIMARY KEY` or `UNIQUE` constraint defined on any table. The stored procedures rely on `(InvoiceID, InvoiceLineID)` and `(OrderID, OrderLineID)` as composite keys but nothing enforces uniqueness. Duplicate rows could silently accumulate. |

**Note:** Fabric Warehouse has limited constraint support (constraints are informational/not enforced). However, declaring them still benefits the query optimizer and documents intent.

### 7.3 HIGH — UPDATE-then-INSERT Instead of MERGE

| Severity | Location | Issue |
|----------|----------|-------|
| **HIGH** | `IncrLoadInvoicedSales`, `IncrLoadSalesOrders` | The UPDATE-then-INSERT pattern scans the source data twice and is not atomic. A concurrent INSERT between the UPDATE and INSERT steps could cause duplicates. |

**Caveat:** Fabric Warehouse does not support T-SQL `MERGE`. The UPDATE-then-INSERT pattern is the correct approach for this platform. However, wrapping in an explicit transaction (if supported) would improve atomicity.

### 7.4 MEDIUM — Redundant NULL Check in INSERT WHERE Clause

| Severity | Location | Issue |
|----------|----------|-------|
| **MEDIUM** | Both stored procedures | `WHERE target.InvoiceID IS NULL AND target.InvoiceLineID IS NULL` — since this is a LEFT JOIN on `(InvoiceID, InvoiceLineID)`, checking IS NULL on just one column is sufficient. Both being NULL is always true together when no match exists. Checking both is redundant and slightly misleading. |

### 7.5 MEDIUM — BETWEEN for Date Range Filtering

| Severity | Location | Issue |
|----------|----------|-------|
| **MEDIUM** | Both stored procedures | `WHERE source.LastUpdated BETWEEN @StartDate AND @EndDate` — `BETWEEN` is inclusive on both ends. With `datetime`/`datetime2` columns, this could re-process rows exactly at the `@StartDate` boundary (already processed in the previous run). This is safe here because the default `@StartDate` is `MAX(LastUpdated)` from the target, so re-processing the boundary row just updates it to the same values. But it's an anti-pattern that can cause subtle bugs if the watermark logic changes. |

### 7.6 MEDIUM — Data Type Mismatch: `rowscopied` Column

| Severity | Location | Issue |
|----------|----------|-------|
| **MEDIUM** | `PipelineOrchestrator_FabricLakehouseGold` | `rowscopied NCHAR(10)` — this is a fixed-length character type for what should be a numeric count. All other orchestrator tables use `INT` for row counts. |

### 7.7 MEDIUM — Stale Comment in Stored Procedure

| Severity | Location | Issue |
|----------|----------|-------|
| **MEDIUM** | `IncrLoadInvoicedSales` | Comment says `-- Find/Replace [lh_fabric_demo] with your Warehouse Name` but the code already uses the correct name. This is a leftover instruction that should be removed. |

### 7.8 LOW — Inconsistent Formatting

| Severity | Location | Issue |
|----------|----------|-------|
| **LOW** | Both stored procedures | Mixed indentation (spaces vs tabs), inconsistent spacing around commas and operators, inconsistent semicolon usage. |
| **LOW** | `IncrLoadSalesOrders` | Starts with `----` (stray comment delimiter). |
| **LOW** | Customer table DDL | Column order is non-standard — key column `CustomerID` appears at position 6 instead of position 1. |
| **LOW** | Pipeline SQL scripts | Long single-line SQL strings are hard to read/maintain. |

### 7.9 LOW — SELECT * in Pipeline Lookups

| Severity | Location | Issue |
|----------|----------|-------|
| **LOW** | Orchestrator lookups | `SELECT * FROM dbo.PipelineOrchestrator_FabricLakehouse` — returns all columns including audit fields that aren't needed by the ForEach loop. Not a performance concern at this scale but violates best practice. |
| **LOW** | Gold Copy source | `SELECT * FROM @{...schema}.@{...table}` — returns all columns from dimension source views. Acceptable for full loads but explicit column lists are preferred. |

### 7.10 LOW — Inconsistent Parameter-Short-Circuit Pattern

| Severity | Location | Issue |
|----------|----------|-------|
| **LOW** | Orchestrator lookups | Lakehouse query uses `1 = @{loadbronze}` (literal on left). Warehouse query uses `@{loaddwh} = 1` (literal on right). Inconsistent style. |

### 7.11 LOW — DELETE Instead of TRUNCATE for Full Load

| Severity | Location | Issue |
|----------|----------|-------|
| **LOW** | Gold pipeline pre-copy | `DELETE FROM ...` is a fully logged operation. `TRUNCATE TABLE` would be faster and use minimal logging. However, Fabric Warehouse may not support TRUNCATE in the pre-copy context. |

### 7.12 INFO — Unused Metadata Table

| Severity | Location | Issue |
|----------|----------|-------|
| **INFO** | `PipelineOrchestrator_FabricLakehouseGold` | This table is defined but not referenced by any pipeline or stored procedure. It may be a remnant of an earlier design or intended for future use. |

---

## 8. Recommendations

### 8.1 Stored Procedure Improvements

| # | Recommendation | Impact |
|---|---------------|--------|
| R1 | Remove stale `Find/Replace` comment from `IncrLoadInvoicedSales` | Readability |
| R2 | Remove stray `----` from top of `IncrLoadSalesOrders` | Readability |
| R3 | Simplify LEFT JOIN WHERE clause — check only one column for IS NULL | Readability |
| R4 | Use `>` instead of `BETWEEN` for `@StartDate` to avoid re-processing boundary rows | Correctness |
| R5 | Add header comment blocks documenting purpose, parameters, and change history | Maintainability |
| R6 | Standardize formatting: consistent indentation, commas, semicolons | Readability |
| R7 | Add `SET XACT_ABORT ON` for consistent error handling | Reliability |

### 8.2 DDL Improvements

| # | Recommendation | Impact |
|---|---------------|--------|
| R8 | Add `PRIMARY KEY` constraints (informational) to all Gold tables | Query optimizer, documentation |
| R9 | Reorder `Customer` columns — put `CustomerID` first | Readability |
| R10 | Fix `rowscopied NCHAR(10)` → `INT` in `PipelineOrchestrator_FabricLakehouseGold` | Correctness |
| R11 | Add NOT NULL to FK columns where data guarantees it (`CustomerID`, `StockItemID`, etc.) | Data integrity |
| R12 | Consider removing unused `PipelineOrchestrator_FabricLakehouseGold` table or documenting its purpose | Maintainability |

### 8.3 Pipeline SQL Improvements

| # | Recommendation | Impact |
|---|---------------|--------|
| R13 | Bracket-quote dynamic identifiers: `[@{schema}].[@{table}]` | Defense-in-depth |
| R14 | Replace `SELECT *` with explicit column lists in orchestrator lookups | Best practice |
| R15 | Standardize parameter short-circuit pattern (`1 = @{param}` vs `@{param} = 1`) | Readability |

---

## 9. Rewritten SQL

### 9.1 `Gold.IncrLoadInvoicedSales` — Rewritten

```sql
/*
================================================================================
  Procedure : Gold.IncrLoadInvoicedSales
  Purpose   : Incrementally load InvoicedSales from lakehouse Silver view to
              warehouse Gold table using UPDATE-then-INSERT pattern.
  Parameters:
      @StartDate DATETIME — Lower bound for LastUpdated filter (inclusive).
                            NULL = auto-detect from MAX(LastUpdated) in target.
      @EndDate   DATETIME — Upper bound for LastUpdated filter (inclusive).
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
    SET XACT_ABORT ON;

    DECLARE @UpdateCount INT, @InsertCount INT;

    -- Default @StartDate to the current high-watermark in the target table
    IF @StartDate IS NULL
    BEGIN
        SELECT @StartDate = ISNULL(MAX(LastUpdated), '2013-01-01')
        FROM [dw_fabric_demo].[Gold].[InvoicedSales];
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
    FROM [dw_fabric_demo].[Gold].[InvoicedSales] AS target
    INNER JOIN [lh_fabric_demo].[Silver].[vInvoicedSales] AS source
        ON  target.InvoiceID     = source.InvoiceID
        AND target.InvoiceLineID = source.InvoiceLineID
    WHERE source.LastUpdated >= @StartDate
      AND source.LastUpdated <= @EndDate;

    SET @UpdateCount = @@ROWCOUNT;

    --------------------------------------------------------------------------
    -- Step 2: INSERT rows that exist in source but not yet in target
    --------------------------------------------------------------------------
    INSERT INTO [dw_fabric_demo].[Gold].[InvoicedSales]
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
    FROM [lh_fabric_demo].[Silver].[vInvoicedSales] AS source
    LEFT JOIN [dw_fabric_demo].[Gold].[InvoicedSales] AS target
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
         FROM [dw_fabric_demo].[Gold].[InvoicedSales]) AS MaxDate;
END;
```

**Changes from original:**
- Removed stale `Find/Replace` comment
- Added header comment block
- Added `SET XACT_ABORT ON`
- Replaced `BETWEEN` with `>= AND <=` (functionally equivalent but more explicit)
- Simplified INSERT WHERE clause — removed redundant `target.InvoiceLineID IS NULL` check
- Used `SET @var = @@ROWCOUNT` instead of `SELECT @var = @@ROWCOUNT` (minor style preference — SET is standard for scalar assignment)
- Standardized formatting: consistent indentation, aligned columns, added section comments
- Added semicolons after all statements

### 9.2 `Gold.IncrLoadSalesOrders` — Rewritten

```sql
/*
================================================================================
  Procedure : Gold.IncrLoadSalesOrders
  Purpose   : Incrementally load SalesOrders from lakehouse Silver view to
              warehouse Gold table using UPDATE-then-INSERT pattern.
  Parameters:
      @StartDate DATETIME — Lower bound for LastUpdated filter (inclusive).
                            NULL = auto-detect from MAX(LastUpdated) in target.
      @EndDate   DATETIME — Upper bound for LastUpdated filter (inclusive).
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
    SET XACT_ABORT ON;

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
    INNER JOIN [lh_fabric_demo].[Silver].[vSalesOrders] AS source
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
    FROM [lh_fabric_demo].[Silver].[vSalesOrders] AS source
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
```

**Changes from original:**
- Removed stray `----` at top of file
- Added header comment block
- Added `SET XACT_ABORT ON`
- Simplified INSERT WHERE clause — removed redundant `target.OrderLineID IS NULL`
- Standardized formatting to match IncrLoadInvoicedSales
- Added semicolons after all statements

### 9.3 Gold Table DDL — Rewritten

```sql
CREATE TABLE [Gold].[InvoicedSales] (
    [InvoiceID]           int            NOT NULL,
    [InvoiceLineID]       int            NOT NULL,
    [InvoiceDate]         date           NULL,
    [CustomerID]          int            NULL,
    [StockItemID]         int            NULL,
    [SalespersonPersonID] int            NULL,
    [Quantity]            int            NULL,
    [ExtendedPrice]       decimal(18,2)  NULL,
    [GrossProfit]         decimal(18,2)  NULL,
    [TaxAmount]           decimal(18,2)  NULL,
    [LastUpdated]         datetime2(6)   NULL
);
```

**Changes:** Reordered columns — key columns first, then date, then FK references, then measures, then audit. No constraint changes (Fabric Warehouse constraints are informational only).

```sql
CREATE TABLE [Gold].[Customer] (
    [CustomerID]            int           NOT NULL,
    [CustomerName]          varchar(100)  NULL,
    [CustomerCategoryID]    int           NULL,
    [BuyingGroupID]         int           NULL,
    [BuyingGroupName]       varchar(50)   NULL,
    [CreditLimit]           decimal(10,2) NULL,
    [IsOnCreditHold]        bit           NULL,
    [PaymentDays]           int           NULL,
    [DeliveryCityID]        int           NULL,
    [DeliveryCity]          varchar(50)   NULL,
    [DeliveryStateProvince] varchar(50)   NULL,
    [DeliveryPostalCode]    varchar(10)   NULL,
    [DeliveryCountry]       varchar(60)   NULL,
    [Region]                varchar(30)   NULL,
    [Subregion]             varchar(30)   NULL,
    [Continent]             varchar(30)   NULL,
    [SalesTerritory]        varchar(50)   NULL,
    [AreaCode]              varchar(3)    NULL,
    [YearsCustomer]         int           NULL
);
```

**Changes:** Reordered — `CustomerID` first, then name, then business attributes, then geographic hierarchy (City→State→Country→Region→Continent), then derived fields last.

### 9.4 Metadata Table Fix

```sql
-- Fix: PipelineOrchestrator_FabricLakehouseGold.rowscopied
-- Before: [rowscopied] NCHAR(10) NULL
-- After:
CREATE TABLE [dbo].[PipelineOrchestrator_FabricLakehouseGold] (
    [pipelinename]      NVARCHAR (100) NOT NULL,
    [sourceschema]      NVARCHAR (50)  NOT NULL,
    [sourcetable]       NVARCHAR (50)  NOT NULL,
    [sourcestartdate]   DATETIME2 (7)  NULL,
    [sourceenddate]     DATETIME2 (7)  NULL,
    [sinktable]         NVARCHAR (100) NULL,
    [loadtype]          NVARCHAR (15)  NOT NULL,
    [tablekey]          NVARCHAR (50)  NULL,
    [tablekey2]         NVARCHAR (50)  NULL,
    [skipload]          BIT            NOT NULL,
    [batchloaddatetime] DATETIME2 (7)  NULL,
    [loadstatus]        NVARCHAR (15)  NULL,
    [rowsread]          INT            NULL,
    [rowscopied]        INT            NULL,       -- Fixed: was NCHAR(10)
    [deltalakeupdated]  INT            NULL,
    [deltalakeinserted] INT            NULL,
    [sinkmaxdatetime]   DATETIME2 (7)  NULL,
    [pipelinestarttime] DATETIME2 (7)  NULL,
    [pipelineendtime]   DATETIME2 (7)  NULL
);
```

---

## 10. Assumptions

1. **Fabric Warehouse limitations:** `MERGE` statement is not supported; `TRUNCATE TABLE` may not be available in pre-copy scripts. The UPDATE-then-INSERT pattern is the correct approach for this platform.
2. **Constraint enforcement:** Fabric Warehouse constraints are informational only (not enforced at write time). Adding PRIMARY KEY constraints is for optimizer hints and documentation.
3. **Cross-database queries:** The stored procedures query across `[dw_fabric_demo]` (warehouse) and `[lh_fabric_demo]` (lakehouse) — this is a supported Fabric cross-database query pattern via the Silver schema views.
4. **Pipeline SQL injection risk:** The dynamic SQL in pipelines is parameterized via metadata tables that are controlled by administrators. The injection risk is theoretical, not practical, but should still be mitigated with bracket quoting.
5. **`PipelineOrchestrator_FabricLakehouseGold`:** Assumed to be unused/vestigial. If it is used by a process outside git (e.g., a Dataflow), the `rowscopied` type fix should be validated before deployment.
6. **Concurrent execution:** The stored procedures are assumed to run sequentially (one at a time per table) as orchestrated by the pipeline ForEach loop. The lack of explicit transactions is acceptable under this assumption.

---

## Summary of Issues by Severity

| Severity | Count | Key Issues |
|----------|-------|------------|
| CRITICAL | 3 | Unquoted dynamic identifiers in pipeline SQL |
| HIGH | 2 | No PK constraints; UPDATE+INSERT not atomic |
| MEDIUM | 4 | Redundant NULL check; BETWEEN boundary; data type mismatch; stale comment |
| LOW | 6 | SELECT *; inconsistent formatting; DELETE vs TRUNCATE |
| INFO | 1 | Unused metadata table |

# Fabric notebook source


# MARKDOWN ********************

# # Incremental Load to Warehouse
# 
# Replaces the Stored Procedure-based incremental load activity in the Load Warehouse Table pipeline.
# Reads changed rows from a lakehouse Delta table and applies a DELETE-matching + INSERT pattern
# to a Fabric Warehouse Gold table.
# 
# This replicates the logic of the warehouse stored procedures (e.g. `Gold.IncrLoadInvoicedSales`,
# `Gold.IncrLoadSalesOrders`) but implemented in PySpark / Spark SQL.
# 
# **Source convention:** `lh_fabric_demo.{sinkTable}` (e.g. `InvoicedSales`)

# CELL ********************

from pyspark.sql.functions import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

sinkSchema = "Gold"
sinkTable = "InvoicedSales"
startDate = "2013-01-01"
endDate = "9999-12-31"
keyColumns = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Determine Key Columns
# Key columns are used for matching source and target rows during the incremental merge.
# If not provided via the `keyColumns` parameter, a built-in mapping is used based on the
# target table name.

# CELL ********************

# Built-in key column mapping per target table
TABLE_KEY_COLUMNS = {
    "InvoicedSales": ["InvoiceID", "InvoiceLineID"],
    "SalesOrders": ["OrderID", "OrderLineID"],
}

# Use parameter if provided, otherwise fall back to built-in mapping
if keyColumns and keyColumns.strip():
    key_cols = [c.strip() for c in keyColumns.split(",")]
else:
    if sinkTable not in TABLE_KEY_COLUMNS:
        raise ValueError(
            f"No key columns configured for table '{sinkTable}'. "
            f"Pass keyColumns parameter as a comma-separated string."
        )
    key_cols = TABLE_KEY_COLUMNS[sinkTable]

print(f"Key columns: {key_cols}")

# Read directly from the lakehouse Delta table (two-part PySpark name)
source_fqn = f"lh_fabric_demo.{sinkTable}"
target_fqn = f"dw_fabric_demo.{sinkSchema}.{sinkTable}"

print(f"Source view: {source_fqn}")
print(f"Target table: {target_fqn}")
print(f"Date range: {startDate} to {endDate}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Read Changed Rows from Lakehouse Delta Table
# Read rows from the lakehouse table where `LastUpdated` falls within the specified date range.
# The lakehouse table columns already match the Gold table schema.

# CELL ********************

# Read changed rows from the lakehouse Delta table
source_df = spark.sql(f"""
    SELECT * FROM {source_fqn}
    WHERE LastUpdated >= '{startDate}' AND LastUpdated <= '{endDate}'
""")
source_df.cache()
source_count = source_df.count()
print(f"Source rows in date range: {source_count}")

# Register as temp view for SQL operations
source_df.createOrReplaceTempView("_incr_source")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Apply Incremental Load (DELETE matching + INSERT)
# This replicates the UPDATE-then-INSERT pattern of the warehouse stored procedures:
# 1. Count existing rows that match source keys (UpdateCount)
# 2. Delete those matching rows from the target
# 3. Insert all source rows (both changed and new)
# 4. Net new rows = InsertCount

# CELL ********************

# Build key join condition for SQL
key_join_condition = " AND ".join([f"t.{k} = s.{k}" for k in key_cols])
key_delete_condition = " AND ".join([f"{target_fqn}.{k} = s.{k}" for k in key_cols])

# Count rows that already exist in target (these are "updates")
update_count_df = spark.sql(f"""
    SELECT COUNT(*) as cnt 
    FROM _incr_source s
    INNER JOIN {target_fqn} t
    ON {key_join_condition}
""")
update_count = update_count_df.first()["cnt"]
insert_count = source_count - update_count
print(f"Rows to update: {update_count}, Rows to insert (new): {insert_count}")

# Delete existing rows that match source keys
if update_count > 0:
    spark.sql(f"""
        DELETE FROM {target_fqn}
        WHERE EXISTS (
            SELECT 1 FROM _incr_source s
            WHERE {key_delete_condition}
        )
    """)
    print(f"Deleted {update_count} existing rows from {target_fqn}")

# Insert all source rows (both updated and new)
if source_count > 0:
    spark.sql(f"""
        INSERT INTO {target_fqn}
        SELECT * FROM _incr_source
    """)
    print(f"Inserted {source_count} rows into {target_fqn}")

source_df.unpersist()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Return Metrics
# Get the current max date from the target table and return execution metrics
# in the same format the pipeline expects.

# CELL ********************

# Get the current max date from the target table
max_date_row = spark.sql(f"SELECT MAX(LastUpdated) as MaxDate FROM {target_fqn}").first()
max_date = str(max_date_row["MaxDate"]) if max_date_row["MaxDate"] else startDate

# Return metrics for pipeline consumption
# Format: status=Succeeded;;UpdateCount=N;;InsertCount=N;;MaxDate=...
result = f"status=Succeeded;;UpdateCount={update_count};;InsertCount={insert_count};;MaxDate={max_date}"
print(f"Result: {result}")
mssparkutils.notebook.exit(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

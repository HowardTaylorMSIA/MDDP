# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Optimize Lakehouse Delta Tables
# 
# This notebook performs maintenance on all Delta tables in the lakehouse:
# 
# 1. **OPTIMIZE with V-Order** – Compacts small files and applies V-Order for faster reads
# 2. **VACUUM** – Removes old, unreferenced data files to reclaim storage
# 
# Reference:
# - [Delta Lake table optimization and V-Order](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-optimization-and-v-order?tabs=sparksql)
# - [Delta Table Maintenance](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-table-maintenance)

# CELL ********************

from datetime import datetime
from delta.tables import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

# Retention period in hours for VACUUM (default 168 = 7 days)
vacuum_retention_hours = 168

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Configuration
# 
# Enable optimized writes and auto-compaction at the Spark session level.
# These settings ensure that future writes also benefit from Delta optimizations.

# CELL ********************

# Enable V-Order and optimized writes at session level
spark.conf.set("spark.sql.parquet.vorder.enabled", "true")
spark.conf.set("sprk.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.binSize", "1073741824")  # 1 GB

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Discover all Delta tables
# 
# Query the lakehouse catalog to get a list of all managed tables.

# CELL ********************

tables_df = spark.sql("SHOW TABLES")
table_list = [row.tableName for row in tables_df.collect()]
print(f"Found {len(table_list)} tables to optimize: {table_list}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## OPTIMIZE with V-Order
# 
# For each table, run `OPTIMIZE ... VORDER` to:
# - **Bin-compact** small Parquet files into larger, optimally sized files (~1 GB)
# - **Apply V-Order** encoding for significantly faster reads in Fabric engines (SQL, Power BI, Spark)
# 
# V-Order is a Fabric-specific write-time optimization that organizes Parquet data for faster reads
# with no cost at read time. It is compatible with all Parquet readers.

# CELL ********************

optimize_results = []

for table_name in table_list:
    start_time = datetime.now()
    try:
        result = spark.sql(f"OPTIMIZE `{table_name}` VORDER")
        metrics = result.collect()
        duration = (datetime.now() - start_time).total_seconds()
        
        # Extract metrics from the OPTIMIZE output
        if metrics and len(metrics) > 0:
            row = metrics[0]
            files_added = row["numFilesAdded"] if "numFilesAdded" in row else "N/A"
            files_removed = row["numFilesRemoved"] if "numFilesRemoved" in row else "N/A"
            optimize_results.append({
                "table": table_name,
                "status": "Success",
                "files_added": files_added,
                "files_removed": files_removed,
                "duration_sec": round(duration, 2)
            })
        else:
            optimize_results.append({
                "table": table_name,
                "status": "Success (no metrics)",
                "files_added": "N/A",
                "files_removed": "N/A",
                "duration_sec": round(duration, 2)
            })
        
        print(f"OPTIMIZE VORDER {table_name}: OK ({duration:.1f}s)")
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        optimize_results.append({
            "table": table_name,
            "status": f"Error: {str(e)[:200]}",
            "files_added": "N/A",
            "files_removed": "N/A",
            "duration_sec": round(duration, 2)
        })
        print(f"OPTIMIZE VORDER {table_name}: FAILED - {str(e)[:200]}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## VACUUM
# 
# Remove old data files no longer referenced by the Delta transaction log.
# Default retention is 7 days (168 hours). This reclaims storage and keeps the table directory clean.
# 
# **Note:** VACUUM does not remove log files — those are managed by Delta checkpointing.

# CELL ********************

vacuum_results = []

for table_name in table_list:
    start_time = datetime.now()
    try:
        delta_table = DeltaTable.forName(spark, table_name)
        delta_table.vacuum(vacuum_retention_hours)
        duration = (datetime.now() - start_time).total_seconds()
        vacuum_results.append({
            "table": table_name,
            "status": "Success",
            "retention_hours": vacuum_retention_hours,
            "duration_sec": round(duration, 2)
        })
        print(f"VACUUM {table_name} (retention={vacuum_retention_hours}h): OK ({duration:.1f}s)")
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        vacuum_results.append({
            "table": table_name,
            "status": f"Error: {str(e)[:200]}",
            "retention_hours": vacuum_retention_hours,
            "duration_sec": round(duration, 2)
        })
        print(f"VACUUM {table_name}: FAILED - {str(e)[:200]}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Summary
# 
# Display the results of the optimization run.

# CELL ********************

# Build summary
summary_lines = []
total_optimize_time = sum(r["duration_sec"] for r in optimize_results)
total_vacuum_time = sum(r["duration_sec"] for r in vacuum_results)
optimize_success = sum(1 for r in optimize_results if r["status"].startswith("Success"))
vacuum_success = sum(1 for r in vacuum_results if r["status"].startswith("Success"))

summary_lines.append(f"Tables processed: {len(table_list)}")
summary_lines.append(f"OPTIMIZE VORDER: {optimize_success}/{len(table_list)} succeeded ({total_optimize_time:.1f}s)")
summary_lines.append(f"VACUUM: {vacuum_success}/{len(table_list)} succeeded ({total_vacuum_time:.1f}s)")

print("\n=== OPTIMIZATION SUMMARY ===")
for line in summary_lines:
    print(line)

print("\n--- OPTIMIZE Details ---")
for r in optimize_results:
    print(f"  {r['table']}: {r['status']} | +{r['files_added']} / -{r['files_removed']} files | {r['duration_sec']}s")

print("\n--- VACUUM Details ---")
for r in vacuum_results:
    print(f"  {r['table']}: {r['status']} | retention={r['retention_hours']}h | {r['duration_sec']}s")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Return summary for pipeline visibility
result = f"tables={len(table_list)};;optimized={optimize_success};;vacuumed={vacuum_success};;total_time={total_optimize_time + total_vacuum_time:.1f}s"
mssparkutils.notebook.exit(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

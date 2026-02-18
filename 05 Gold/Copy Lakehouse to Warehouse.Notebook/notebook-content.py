# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "d3952fd1-aa92-4d42-84fd-a99afcc6614d",
# META       "default_lakehouse_name": "lh_fabric_demo",
# META       "default_lakehouse_workspace_id": "ecfcf483-666f-4267-9456-d09b370c4a12",
# META       "known_lakehouses": [
# META         {
# META           "id": "d3952fd1-aa92-4d42-84fd-a99afcc6614d"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Copy Lakehouse to Warehouse
# 
# Replaces the Copy Data activity in the Load Warehouse Table pipeline.
# Reads from a Silver view in the warehouse (which references the lakehouse Delta tables)
# and writes to a Fabric Warehouse Gold table.
# Performs a DELETE + INSERT pattern for full load replacement.

# CELL ********************

from pyspark.sql.functions import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

sourceSchema = "dbo"
sourceTable = "Invoices"
sinkSchema = "Gold"
sinkTable = "InvoicedSales"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Read from Warehouse Silver View
# The Silver views now live in `dw_fabric_demo.Silver` and reference the lakehouse
# Delta tables with the correct column names/renames for the Gold layer.
# We simply SELECT * from the view — it already outputs the right schema.

# CELL ********************

source_fqn = f"dw_fabric_demo.{sourceSchema}.{sourceTable}"
target_fqn = f"dw_fabric_demo.{sinkSchema}.{sinkTable}"

# Read from the Silver view in the warehouse
df = spark.sql(f"SELECT * FROM {source_fqn}")

# Cache to avoid re-reading during write
df.cache()
rowsCopied = df.count()
print(f"Source: {source_fqn}")
print(f"Rows read: {rowsCopied}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Write to Warehouse
# Delete existing rows and insert new data into the warehouse Gold schema table.
# Uses cross-database queries with the attached warehouse resource.

# CELL ********************

# Delete existing data from the warehouse target table
spark.sql(f"DELETE FROM {target_fqn}")
print(f"Deleted existing data from {target_fqn}")

# Create a temporary view and insert into warehouse
df.createOrReplaceTempView("_staging_data")
spark.sql(f"INSERT INTO {target_fqn} SELECT * FROM _staging_data")
print(f"Inserted {rowsCopied} rows into {target_fqn}")

df.unpersist()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Return metrics for pipeline consumption
# Format: status=Succeeded;;rowsCopied=N
result = f"status=Succeeded;;rowsCopied={rowsCopied}"
mssparkutils.notebook.exit(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

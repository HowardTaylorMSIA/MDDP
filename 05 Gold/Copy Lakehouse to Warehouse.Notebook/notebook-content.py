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
# Reads from a lakehouse Delta table and writes to a Fabric Warehouse table.
# Performs a DELETE + INSERT pattern for full load replacement.

# METADATA ********************

# META {
# META   "language": "markdown",
# META   "language_group": "synapse_pyspark"
# META }

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

# ## Read from Lakehouse
# Read the source table from the default lakehouse (lh_fabric_demo).

# METADATA ********************

# META {
# META   "language": "markdown",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Read the source table from the lakehouse
df = spark.sql(f"SELECT * FROM lh_fabric_demo.{sourceSchema}.{sourceTable}")

# Cache to avoid re-reading during write
df.cache()
rowsCopied = df.count()
print(f"Rows read from lakehouse: {rowsCopied}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Write to Warehouse
# Delete existing rows and insert new data into the warehouse Gold schema table.
# Uses cross-database queries with the attached warehouse resource.

# METADATA ********************

# META {
# META   "language": "markdown",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Delete existing data from the warehouse target table
spark.sql(f"DELETE FROM dw_fabric_demo.{sinkSchema}.{sinkTable}")
print(f"Deleted existing data from dw_fabric_demo.{sinkSchema}.{sinkTable}")

# Create a temporary view and insert into warehouse
df.createOrReplaceTempView("_staging_data")
spark.sql(f"INSERT INTO dw_fabric_demo.{sinkSchema}.{sinkTable} SELECT * FROM _staging_data")
print(f"Inserted {rowsCopied} rows into dw_fabric_demo.{sinkSchema}.{sinkTable}")

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

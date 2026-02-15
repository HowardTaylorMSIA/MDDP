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

# CELL ********************

from delta.tables import *
from pyspark.sql.functions import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

lakehousePath = "abfss://85bfc254-9abf-46cc-b1fe-943ec35b3460@msit-onelake.dfs.fabric.microsoft.com/c02dea28-20ca-432b-b6e8-39d0be76f540"
tableName = "Invoices"
tableKey = "InvoiceID"
tableKey2 = None
dateColumn = "LastEditedWhen"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# deltaTablePath = f"{lakehousePath}/Tables/{tableName}" 
deltaTablePath = f"{lakehousePath}/Tables/{tableName}" 
# print(deltaTablePath)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

parquetFilePath = f"{lakehousePath}/Files/incremental/{tableName}/{tableName}.parquet"
# print(parquetFilePath)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df2 = spark.read.parquet(parquetFilePath)
# display(df2)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if tableKey2 is None:
    mergeKeyExpr = f"t.{tableKey} = s.{tableKey}"
else:
    mergeKeyExpr = f"t.{tableKey} = s.{tableKey} AND t.{tableKey2} = s.{tableKey2}"    

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Check if table already exists; if it does, do an upsert and return how many rows were inserted and update; if it does not exist, return how many rows were inserted

# CELL ********************

if mssparkutils.fs.exists(deltaTablePath) and DeltaTable.isDeltaTable(spark,deltaTablePath):
    deltaTable = DeltaTable.forPath(spark,deltaTablePath)
    deltaTable.alias("t").merge(
        df2.alias("s"),
        mergeKeyExpr
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    history = deltaTable.history(1).select("operationMetrics")
    operationMetrics = history.collect()[0]["operationMetrics"]
    numInserted = operationMetrics["numTargetRowsInserted"]
    numUpdated = operationMetrics["numTargetRowsUpdated"]
else:
    df2.write.format("delta").mode("overwrite").saveAsTable(tableName)
    numInserted = df2.count()
    numUpdated = 0

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Get the latest date loaded into the table - this will be used for watermarking; return the max date, the number of rows inserted and number updated

# CELL ********************

deltaTablePath = f"{lakehousePath}/Tables/{tableName}"
if mssparkutils.fs.exists(deltaTablePath):
    df3 = spark.read.format("delta").load(deltaTablePath)
else:
    df3 = spark.table(tableName)
maxdate = df3.agg(max(dateColumn)).collect()[0][0]
# print(maxdate)
if maxdate is not None and hasattr(maxdate, 'strftime'):
    maxdate_str = maxdate.strftime("%Y-%m-%d %H:%M:%S")
elif maxdate is not None:
    maxdate_str = str(maxdate)
else:
    maxdate_str = "1900-01-01 00:00:00"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

result = "maxdate="+maxdate_str +  ";;numInserted="+str(numInserted)+  ";;numUpdated="+str(numUpdated)
# result = {"maxdate": maxdate_str, "numInserted": numInserted, "numUpdated": numUpdated}
mssparkutils.notebook.exit(str(result))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************


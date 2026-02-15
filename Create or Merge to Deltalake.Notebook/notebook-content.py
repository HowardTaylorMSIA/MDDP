# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "fcc6614d-a99a-84fd-4d42-aa92d3952fd1",
# META       "default_lakehouse_name": "lh_fabric_demo",
# META       "default_lakehouse_workspace_id": "00000000-0000-0000-0000-000000000000",
# META       "known_lakehouses": [
# META         {
# META           "id": "fcc6614d-a99a-84fd-4d42-aa92d3952fd1"
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

if DeltaTable.isDeltaTable(spark,deltaTablePath):
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
df3 = spark.read.format("delta").load(deltaTablePath)
maxdate = df3.agg(max(dateColumn)).collect()[0][0]
# print(maxdate)
maxdate_str = maxdate.strftime("%Y-%m-%d %H:%M:%S")

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


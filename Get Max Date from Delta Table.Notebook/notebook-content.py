# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse_name": "",
# META       "default_lakehouse_workspace_id": "",
# META       "known_lakehouses": []
# META     }
# META   }
# META }

# CELL ********************

# Welcome to your new notebooks
# Type here in the cell editor to add code!
from delta.tables import *
from pyspark.sql.functions import *


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

lakehousePath = "abfss://ecfcf483-666f-4267-9456-d09b370c4a12@onelake.dfs.fabric.microsoft.com/d3952fd1-aa92-4d42-84fd-a99afcc6614d"
tableName = "Colors"
tableKey = "ColorID"
dateColumn = "ValidTo"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

deltaTablePath = f"{lakehousePath}/Tables/{tableName}" #fill in your delta table path 
# print(deltaTablePath)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Get maxdate and number of records in table

# CELL ********************

if mssparkutils.fs.exists(deltaTablePath):
    df = spark.read.format("delta").load(deltaTablePath)
    maxdate = df.agg(max(dateColumn)).collect()[0][0]
    rowcount = df.count()
    maxdate_str = maxdate.strftime("%Y-%m-%d %H:%M:%S")
    result = "maxdate="+maxdate_str +  "|rowcount="+str(rowcount)
else:
    result = "maxdate=1900-01-01 00:00:00|rowcount=0"

mssparkutils.notebook.exit(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

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

# Welcome to your new notebook
# Type here in the cell editor to add code!
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

startyear = 2013
endyear = 2025

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

lakehousePath = "abfss://ecfcf483-666f-4267-9456-d09b370c4a12@onelake.dfs.fabric.microsoft.com/d3952fd1-aa92-4d42-84fd-a99afcc6614d"
deltaTablePath = f"{lakehousePath}/Tables/Calendar" 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark = SparkSession.builder.appName("Calendar").getOrCreate()

# Set the time parser policy to LEGACY
# spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

# Create a DataFrame with a range of dates
dates = spark.range(
    (datetime(endyear, 12, 31) - datetime(startyear, 1, 1)).days + 1
).select(
    (date_add(lit(f"{startyear}-01-01"), col("id").cast("int"))).alias("date")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Select the desired columns
calendardf = dates.select(
    "date",
    dayofmonth("date").alias("daynum"),
    dayofweek("date").alias("dayofweeknum"),
    # date_format("date", "e").alias("dayofweeknum"),
    date_format("date", "EEEE").alias("dayofweekname"),
    month("date").alias("monthnum"),
    date_format("date", "MMMM").alias("monthname"),
    quarter("date").alias("quarternum"),
    concat(lit("Q"), quarter("date")).alias("quartername"),
    year("date").alias("year")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Show the resulting DataFrame
# calendardf.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

calendardf.write.format("delta").mode("overwrite").save(deltaTablePath)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

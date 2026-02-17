# Fabric notebook source


# MARKDOWN ********************

# # Copy WWI to Lakehouse
# 
# Replaces the Copy Data activity in the Get WWImporters Data pipeline.
# Reads from Azure SQL (WWI) via JDBC and writes to the lakehouse as either
# a Delta table (full load) or a staged Parquet file (incremental load).
# 
# **Important:** Update `serverName` with the actual Azure SQL server FQDN before first use.

# CELL ********************

from pyspark.sql.functions import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

serverName = "azuresqlht.database.windows.net"
databaseName = "WWI"
sqlSourceSchema = "Sales"
sqlSourceTable = "Invoices"
sourceColumns = "*"
datePredicate = "LastEditedWhen >= '2013-01-01'"
sinkTableName = "Invoices"
loadType = "full"
lakehousePath = "abfss://ecfcf483-666f-4267-9456-d09b370c4a12@onelake.dfs.fabric.microsoft.com/d3952fd1-aa92-4d42-84fd-a99afcc6614d"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Read from Azure SQL via JDBC
# Uses Azure AD token authentication to connect to Azure SQL Database (WWI).

# CELL ********************

# Build SQL query with source columns and date predicate
sqlQuery = f"(SELECT {sourceColumns} FROM {sqlSourceSchema}.{sqlSourceTable} WHERE {datePredicate}) AS src"

# Get Azure AD access token for SQL authentication
accessToken = mssparkutils.credentials.getToken("https://database.windows.net/")

# Build JDBC URL
jdbcUrl = f"jdbc:sqlserver://{serverName};database={databaseName};encrypt=true;trustServerCertificate=false"

# Read from Azure SQL via JDBC
df = spark.read \
    .format("jdbc") \
    .option("url", jdbcUrl) \
    .option("dbtable", sqlQuery) \
    .option("accessToken", accessToken) \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .load()

# Cache to avoid reading from JDBC twice (once for count, once for write)
df.cache()
rowsRead = df.count()
print(f"Rows read from source: {rowsRead}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Write to Lakehouse
# - **Full load**: Overwrite the Delta table directly with V-Order optimization
# - **Incremental load**: Write to a Parquet staging area for downstream merge via the Create or Merge to Deltalake notebook

# CELL ********************

if loadType == "full":
    # Full load: overwrite the Delta table with V-Order optimization
    df.write.format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .option("vorder.enabled", "true") \
        .saveAsTable(sinkTableName)
    rowsCopied = rowsRead
    print(f"Full load: wrote {rowsCopied} rows to Delta table '{sinkTableName}'")
else:
    # Incremental load: write to Parquet staging area
    parquetPath = f"{lakehousePath}/Files/incremental/{sinkTableName}/{sinkTableName}.parquet"
    df.write.mode("overwrite").parquet(parquetPath)
    rowsCopied = rowsRead
    print(f"Incremental load: wrote {rowsCopied} rows to Parquet staging at '{parquetPath}'")

df.unpersist()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Return metrics for pipeline consumption
# Format: status=Succeeded;;rowsRead=N;;rowsCopied=N
result = f"status=Succeeded;;rowsRead={rowsRead};;rowsCopied={rowsCopied}"
mssparkutils.notebook.exit(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

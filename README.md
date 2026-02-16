# mddp — Metadata-Driven Data Platform

A metadata-driven data pipeline solution built on Microsoft Fabric, loading data from Azure SQL (WWI) into a Lakehouse (bronze), then into a Warehouse (gold), with full orchestration, incremental loading, and Delta Lake optimization.

## Architecture

```
Azure SQL (WWI) ──► Lakehouse (Bronze) ──► Calendar ──► Optimize ──► Warehouse (Gold) ──► Semantic Model ──► Reports
                         │                                                │
                    FabricMetadataOrchestration                    Stored Procedures
                      (control database)                        (IncrLoad / FullLoad)
```

## Workspace Folder Structure

Fabric workspace folders are a **UI-only concept** — they are configured within the Fabric workspace, not through the git repo structure. All artifact folders must remain at the root of the git sync directory.

The recommended workspace folder layout (created manually in Fabric) mirrors the pipeline execution flow for easy navigation and Taskflow alignment:

```
📁 1. Orchestration
│   └── orchestrator Load WWI to Fabric          (Pipeline - entry point)
│
📁 2. Bronze
│   ├── Get WWImporters Data direct               (Pipeline - child, full + incremental)
│   ├── Get Max Date from Delta Table             (Notebook - watermark lookup)
│   ├── Create or Merge to Deltalake              (Notebook - upsert to Delta)
│   └── lh_fabric_demo                            (Lakehouse - bronze Delta tables)
│
📁 3. Calendar
│   └── Build Calendar                            (Notebook - date dimension)
│
📁 4. Optimization
│   └── Optimize Lakehouse Tables                 (Notebook - OPTIMIZE VORDER + VACUUM)
│
📁 5. Gold
│   ├── Load Warehouse Table                      (Pipeline - child, full + incremental SP)
│   └── dw_fabric_demo                            (Warehouse - Gold schema)
│
📁 6. Metadata
│   └── FabricMetadataOrchestration               (SQL Database - pipeline config)
│
📁 7. Monitoring
│   └── My Activator                              (Reflex - alerting)
│
📁 8. Semantic Model
│   └── (Power BI semantic model - future)
│
📁 9. Reports
│   └── (Power BI reports - future)
```

> **Note:** To set up these folders, create them in the Fabric workspace UI and drag items into them. This is safe because all cross-references use GUIDs — moving items between folders never breaks pipeline or notebook references.

### Taskflow Mapping

Each folder maps to a stage in the end-to-end Taskflow:

| Stage | Folder | Trigger | Description |
|-------|--------|---------|-------------|
| 1 | Orchestration | Manual / Schedule | Reads metadata, dispatches child pipelines |
| 2 | Bronze | Orchestrator ForEach | Loads source tables into lakehouse Delta tables |
| 3 | Calendar | After Bronze | Builds/refreshes date dimension table |
| 4 | Optimization | After Calendar | Runs OPTIMIZE VORDER + VACUUM on all Delta tables |
| 5 | Gold | After Optimization | Loads warehouse Gold schema via stored procedures |
| 6 | Metadata | Always available | Control tables that drive pipeline behavior |
| 7 | Monitoring | Event-driven | Reflex alerts on pipeline events |
| 8 | Semantic Model | After Gold | Power BI dataset over warehouse Gold tables |
| 9 | Reports | On demand | Power BI reports and dashboards |

## Pipeline Parameters

The orchestrator pipeline exposes these parameters to control execution:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startyear` | int | 2013 | Calendar start year |
| `endyear` | int | 2027 | Calendar end year |
| `loadbronze` | int | 1 | Load bronze lakehouse tables (0 = skip) |
| `loadcalendar` | int | 1 | Build calendar dimension (0 = skip) |
| `loadoptimize` | int | 1 | Run Delta table optimization (0 = skip) |
| `loaddwh` | int | 0 | Load warehouse Gold tables (0 = skip) |
| `vacuum_retention_hours` | int | 168 | VACUUM retention period (hours, default 7 days) |

## Key Design Decisions

- **Metadata-driven**: Pipeline behavior (tables, load types, date ranges) is controlled by SQL tables in `FabricMetadataOrchestration`, not hardcoded
- **Incremental + Full load**: Each table can be configured for full or incremental loading via the `loadtype` column
- **V-Order optimization**: Delta tables are compacted with V-Order encoding for optimal read performance across Spark, SQL, and Power BI
- **All cross-references use GUIDs**: Notebook IDs, pipeline IDs, artifact IDs, and connection IDs — folder reorganization never breaks references

## Capacity Note

> **ForEach Throttling:** The orchestrator pipeline's ForEach loop is limited to `batchCount: 2` to avoid HTTP 429/430 throttling errors on Fabric F2 capacity. If running on F8 or higher, you can increase or remove this limit to enable full parallel processing of all batches.
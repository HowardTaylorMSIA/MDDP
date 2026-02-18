# Silver Views — Manual Deploy

These views must be **manually created** in the `dw_fabric_demo` warehouse.
They cannot be deployed via Git sync because the cross-database references
to `lh_fabric_demo` are not resolvable at deployment time (causes `DmsImportDatabaseException`).

## Deploy Order

1. Run `Silver.sql` first (creates the schema)
2. Run all `v*.sql` files (creates the views)

## What They Do

Each view is a simple `SELECT *` from the corresponding lakehouse Delta table,
providing a Silver layer inside the warehouse for the Gold stored procedures
and Copy Data activities to read from.

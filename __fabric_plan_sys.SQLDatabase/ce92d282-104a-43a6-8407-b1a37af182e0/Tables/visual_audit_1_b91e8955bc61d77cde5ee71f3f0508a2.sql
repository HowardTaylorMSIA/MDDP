CREATE TABLE [ce92d282-104a-43a6-8407-b1a37af182e0].[visual_audit_1_b91e8955bc61d77cde5ee71f3f0508a2] (
    [id]                       BIGINT          IDENTITY (1, 1) NOT NULL,
    [rowId]                    NVARCHAR (2048) NOT NULL,
    [colId]                    NVARCHAR (2048) NOT NULL,
    [scenarioGuid]             NVARCHAR (255)  NULL,
    [measureGuid]              NVARCHAR (255)  NULL,
    [filterContextHash]        NVARCHAR (255)  NULL,
    [action]                   NVARCHAR (255)  NULL,
    [meta]                     NVARCHAR (MAX)  NULL,
    [oldValue]                 NVARCHAR (MAX)  NULL,
    [newValue]                 NVARCHAR (MAX)  NULL,
    [updatedAt]                INT             NOT NULL,
    [updatedByUPN]             NVARCHAR (320)  NOT NULL,
    [updatedBy]                NVARCHAR (128)  NOT NULL,
    [dim_CustomerCustomerName] NVARCHAR (255)  NULL,
    [dim_SalespersonFullName]  NVARCHAR (255)  NULL,
    PRIMARY KEY CLUSTERED ([id] ASC)
);


GO

CREATE NONCLUSTERED INDEX [visual_audit_1_b91e8955bc61d77cde5ee71f3f0508a2_dim_CustomerCustomerName]
    ON [ce92d282-104a-43a6-8407-b1a37af182e0].[visual_audit_1_b91e8955bc61d77cde5ee71f3f0508a2]([dim_CustomerCustomerName] ASC);


GO

CREATE NONCLUSTERED INDEX [visual_audit_1_b91e8955bc61d77cde5ee71f3f0508a2_dim_SalespersonFullName]
    ON [ce92d282-104a-43a6-8407-b1a37af182e0].[visual_audit_1_b91e8955bc61d77cde5ee71f3f0508a2]([dim_SalespersonFullName] ASC);


GO


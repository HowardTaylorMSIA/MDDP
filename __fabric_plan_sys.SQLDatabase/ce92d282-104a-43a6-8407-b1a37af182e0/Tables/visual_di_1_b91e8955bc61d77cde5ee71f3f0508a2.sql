CREATE TABLE [ce92d282-104a-43a6-8407-b1a37af182e0].[visual_di_1_b91e8955bc61d77cde5ee71f3f0508a2] (
    [id]                       BIGINT           IDENTITY (1, 1) NOT NULL,
    [rowId]                    NVARCHAR (255)   NOT NULL,
    [colId]                    NVARCHAR (255)   NOT NULL,
    [scenarioId]               INT              NULL,
    [filterContextHash]        NVARCHAR (255)   NULL,
    [updatedAt]                INT              NOT NULL,
    [updatedBy]                NVARCHAR (128)   NOT NULL,
    [dim_CustomerCustomerName] NVARCHAR (255)   NULL,
    [dim_SalespersonFullName]  NVARCHAR (255)   NULL,
    [measure_1]                DECIMAL (30, 10) NULL,
    [measure_1_meta]           NVARCHAR (255)   NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    UNIQUE NONCLUSTERED ([rowId] ASC, [colId] ASC, [scenarioId] ASC, [filterContextHash] ASC)
);


GO

CREATE NONCLUSTERED INDEX [visual_di_1_b91e8955bc61d77cde5ee71f3f0508a2_dim_CustomerCustomerName]
    ON [ce92d282-104a-43a6-8407-b1a37af182e0].[visual_di_1_b91e8955bc61d77cde5ee71f3f0508a2]([dim_CustomerCustomerName] ASC);


GO

CREATE NONCLUSTERED INDEX [visual_di_1_b91e8955bc61d77cde5ee71f3f0508a2_dim_SalespersonFullName]
    ON [ce92d282-104a-43a6-8407-b1a37af182e0].[visual_di_1_b91e8955bc61d77cde5ee71f3f0508a2]([dim_SalespersonFullName] ASC);


GO


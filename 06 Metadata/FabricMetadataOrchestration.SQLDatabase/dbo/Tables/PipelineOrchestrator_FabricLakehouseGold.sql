CREATE TABLE [dbo].[PipelineOrchestrator_FabricLakehouseGold] (
    [pipelinename]      NVARCHAR (100) NOT NULL,
    [sourceschema]      NVARCHAR (50)  NOT NULL,
    [sourcetable]       NVARCHAR (50)  NOT NULL,
    [sourcestartdate]   DATETIME2 (7)  NULL,
    [sourceenddate]     DATETIME2 (7)  NULL,
    [sinktable]         NVARCHAR (100) NULL,
    [loadtype]          NVARCHAR (15)  NOT NULL,
    [tablekey]          NVARCHAR (50)  NULL,
    [tablekey2]         NVARCHAR (50)  NULL,
    [skipload]          BIT            NOT NULL,
    [batchloaddatetime] DATETIME2 (7)  NULL,
    [loadstatus]        NVARCHAR (15)  NULL,
    [rowsread]          INT            NULL,
    [rowscopied]        NCHAR (10)     NULL,
    [deltalakeupdated]  INT            NULL,
    [deltalakeinserted] INT            NULL,
    [sinkmaxdatetime]   DATETIME2 (7)  NULL,
    [pipelinestarttime] DATETIME2 (7)  NULL,
    [pipelineendtime]   DATETIME2 (7)  NULL
);


GO


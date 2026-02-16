CREATE TABLE [dbo].[PipelineOrchestrator_FabricLakehouse] (
    [pipelinename]        NVARCHAR (100) NOT NULL,
    [sqlsourceschema]     NVARCHAR (50)  NOT NULL,
    [sqlsourcetable]      NVARCHAR (50)  NOT NULL,
    [sourcecolumns]       NVARCHAR (MAX) NULL,
    [sqlsourcedatecolumn] NVARCHAR (50)  NULL,
    [sourcekeycolumn]     NVARCHAR (50)  NULL,
    [sqlstartdate]        SMALLDATETIME  NULL,
    [sqlenddate]          SMALLDATETIME  NULL,
    [sinktablename]       NVARCHAR (100) NULL,
    [loadtype]            NVARCHAR (15)  NOT NULL,
    [skipload]            BIT            NOT NULL,
    [batchloaddatetime]   DATETIME2 (7)  NULL,
    [loadstatus]          NVARCHAR (15)  NULL,
    [rowsread]            INT            NULL,
    [rowscopied]          INT            NULL,
    [deltalakeinserted]   INT            NULL,
    [deltalakeupdated]    INT            NULL,
    [sqlmaxdatetime]      DATETIME2 (7)  NULL,
    [pipelinestarttime]   DATETIME2 (7)  NULL,
    [pipelineendtime]     DATETIME2 (7)  NULL
);


GO


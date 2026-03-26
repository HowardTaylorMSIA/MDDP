CREATE TABLE [dbo].[wb_demo] (
    [IrId]                 INT             IDENTITY (1, 1) NOT NULL,
    [IrScenario]           NVARCHAR (512)  NULL,
    [Customername]         NVARCHAR (512)  NULL,
    [Fullname]             NVARCHAR (512)  NULL,
    [ValueColumnName]      NVARCHAR (512)  NULL,
    [Value]                NUMERIC (25, 2) NULL,
    [ValueText]            NVARCHAR (MAX)  NULL,
    [LastUpdatedAt]        DATETIME2 (7)   NULL,
    [LastUpdatedBy]        NVARCHAR (512)  NULL,
    [Source]               NVARCHAR (512)  NULL,
    [IrNotes]              NVARCHAR (MAX)  NULL,
    [IrComments]           NVARCHAR (MAX)  NULL,
    [IrCellMeta]           NVARCHAR (MAX)  NULL,
    [IrWritebackUser]      NVARCHAR (512)  NULL,
    [IrWritebackTimestamp] DATETIME2 (7)   NULL,
    PRIMARY KEY CLUSTERED ([IrId] ASC)
);


GO


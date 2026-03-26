CREATE TABLE [dbo].[wb_payload_1] (
    [Customername]      NVARCHAR (512) NULL,
    [Fullname]          NVARCHAR (512) NULL,
    [ValueColumnName]   NVARCHAR (512) NULL,
    [Value]             NVARCHAR (MAX) NULL,
    [Source]            NVARCHAR (512) NULL,
    [IrNotes]           NVARCHAR (MAX) NULL,
    [IrScenario]        NVARCHAR (512) NULL,
    [CellId]            NVARCHAR (512) NULL,
    [IsAggregated]      TINYINT        CONSTRAINT [wb_payload_1_isaggregated_default] DEFAULT ('1') NULL,
    [FilterContextHash] NVARCHAR (512) NULL,
    [ExecutionId]       NVARCHAR (512) NULL,
    [IrId]              NVARCHAR (512) NULL
);


GO


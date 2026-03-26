CREATE TABLE [333df339-382f-479f-aa84-2b485b14aaa9].[ib_query_transformation_steps] (
    [id]        INT            IDENTITY (1, 1) NOT NULL,
    [notes]     NVARCHAR (MAX) NULL,
    [meta]      NVARCHAR (MAX) NULL,
    [queryId]   INT            NOT NULL,
    [stepIndex] INT            NOT NULL,
    [status]    INT            CONSTRAINT [DF_ceb667e5d22fef8bb98da39b2b6] DEFAULT ((10)) NOT NULL,
    [createdBy] NVARCHAR (128) NOT NULL,
    [updatedBy] NVARCHAR (128) NOT NULL,
    [createdAt] INT            NOT NULL,
    [updatedAt] INT            NOT NULL,
    CONSTRAINT [PK_28b762220d574fa6dc14ddd0d3a] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_8a9b406684b6d9fc5b0e6a20189] FOREIGN KEY ([queryId]) REFERENCES [333df339-382f-479f-aa84-2b485b14aaa9].[ib_queries] ([id]) ON DELETE CASCADE
);


GO

CREATE NONCLUSTERED INDEX [idx_ib_query_transformation_steps_queryId]
    ON [333df339-382f-479f-aa84-2b485b14aaa9].[ib_query_transformation_steps]([queryId] ASC);


GO


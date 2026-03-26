CREATE TABLE [333df339-382f-479f-aa84-2b485b14aaa9].[ib_source] (
    [id]             INT            IDENTITY (1, 1) NOT NULL,
    [type]           INT            NOT NULL,
    [meta]           NVARCHAR (MAX) NOT NULL,
    [workloadItemId] NVARCHAR (36)  NOT NULL,
    [visualId]       INT            NULL,
    [name]           VARCHAR (2048) NOT NULL,
    [filePath]       VARCHAR (255)  NULL,
    [status]         INT            CONSTRAINT [DF_208052c910ea47b876840dd43dd] DEFAULT ((10)) NOT NULL,
    [createdBy]      NVARCHAR (128) NOT NULL,
    [updatedBy]      NVARCHAR (128) NOT NULL,
    [createdAt]      INT            NOT NULL,
    [updatedAt]      INT            NOT NULL,
    CONSTRAINT [PK_d74732762213731a98c7acce623] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_857e1cee10c832cdd99e84b5e68] FOREIGN KEY ([visualId]) REFERENCES [333df339-382f-479f-aa84-2b485b14aaa9].[visual] ([id]) ON DELETE CASCADE
);


GO

CREATE NONCLUSTERED INDEX [idx_ib_source_visualId]
    ON [333df339-382f-479f-aa84-2b485b14aaa9].[ib_source]([visualId] ASC);


GO

CREATE NONCLUSTERED INDEX [idx_ib_source_workloadItemId]
    ON [333df339-382f-479f-aa84-2b485b14aaa9].[ib_source]([workloadItemId] ASC);


GO


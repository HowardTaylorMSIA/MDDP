CREATE TABLE [cce51655-5aaf-4fb2-9127-5772b6e43a21].[powertable_row_access_filters] (
    [id]               INT            IDENTITY (1, 1) NOT NULL,
    [sourceSettingsId] INT            NOT NULL,
    [name]             VARCHAR (255)  NOT NULL,
    [filterType]       INT            NOT NULL,
    [filter]           NVARCHAR (MAX) NOT NULL,
    [status]           INT            NOT NULL,
    [createdBy]        NVARCHAR (128) NOT NULL,
    [updatedBy]        NVARCHAR (128) NOT NULL,
    [createdAt]        INT            NOT NULL,
    [updatedAt]        INT            NOT NULL,
    CONSTRAINT [PK_625384bae05eeba8810fe06b10d] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_4cf5fc924af7310bf47527e6997] FOREIGN KEY ([sourceSettingsId]) REFERENCES [cce51655-5aaf-4fb2-9127-5772b6e43a21].[powertable_source_settings] ([id])
);


GO


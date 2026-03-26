CREATE TABLE [cce51655-5aaf-4fb2-9127-5772b6e43a21].[powertable_lookup_config] (
    [id]                  INT            IDENTITY (1, 1) NOT NULL,
    [sourceEntityId]      INT            NOT NULL,
    [sourceEntityType]    INT            NOT NULL,
    [relationshipMapping] VARCHAR (MAX)  NOT NULL,
    [lookupsourceId]      INT            NOT NULL,
    [lookupKey]           VARCHAR (255)  NULL,
    [lookupValue]         VARCHAR (MAX)  NULL,
    [sourceId]            INT            NOT NULL,
    [status]              INT            CONSTRAINT [DF_9cdd5919af14d6c8ded1258b9ca] DEFAULT ((10)) NOT NULL,
    [createdBy]           NVARCHAR (128) NOT NULL,
    [updatedBy]           NVARCHAR (128) NOT NULL,
    [createdAt]           INT            NOT NULL,
    [updatedAt]           INT            NOT NULL,
    CONSTRAINT [PK_39a062b26e8fd0d3e2bf74d01c9] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_44ada73e90ba9eb593ec9ae3d0c] FOREIGN KEY ([sourceId]) REFERENCES [cce51655-5aaf-4fb2-9127-5772b6e43a21].[powertable_source] ([id])
);


GO


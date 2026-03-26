CREATE TABLE [b879171e-ba93-4042-9c71-e044767aab28].[powertable_row_access_filter_users] (
    [id]                INT            IDENTITY (1, 1) NOT NULL,
    [rowAccessFilterId] INT            NOT NULL,
    [accessEntityId]    VARCHAR (128)  NOT NULL,
    [accessEntityType]  INT            NOT NULL,
    [status]            INT            NOT NULL,
    [createdBy]         NVARCHAR (128) NOT NULL,
    [updatedBy]         NVARCHAR (128) NOT NULL,
    [createdAt]         INT            NOT NULL,
    [updatedAt]         INT            NOT NULL,
    CONSTRAINT [PK_027672bb5fbf96830a92634333b] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_eeb65a0747b2c167501dff56d1a] FOREIGN KEY ([rowAccessFilterId]) REFERENCES [b879171e-ba93-4042-9c71-e044767aab28].[powertable_row_access_filters] ([id])
);


GO


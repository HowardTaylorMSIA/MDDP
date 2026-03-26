CREATE TABLE [b879171e-ba93-4042-9c71-e044767aab28].[data_input_column] (
    [id]                   INT            IDENTITY (1, 1) NOT NULL,
    [visualId]             INT            NOT NULL,
    [measureGuid]          VARCHAR (255)  NOT NULL,
    [dataInputType]        INT            NOT NULL,
    [name]                 VARCHAR (255)  NOT NULL,
    [description]          VARCHAR (2048) NULL,
    [columnMeta]           NVARCHAR (MAX) NULL,
    [boundToFilterContext] INT            CONSTRAINT [DF_904838640d21f75be1210ff7e07] DEFAULT ((20)) NOT NULL,
    [status]               INT            CONSTRAINT [DF_99b4b205612ae34711d224e7aea] DEFAULT ((10)) NOT NULL,
    [createdBy]            NVARCHAR (128) NOT NULL,
    [updatedBy]            NVARCHAR (128) NOT NULL,
    [createdAt]            INT            NOT NULL,
    [updatedAt]            INT            NOT NULL,
    CONSTRAINT [PK_e757521d9dd64e754591afabac8] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_2f2ba9690ea788805bf78ae17a1] FOREIGN KEY ([visualId]) REFERENCES [b879171e-ba93-4042-9c71-e044767aab28].[visual] ([id])
);


GO


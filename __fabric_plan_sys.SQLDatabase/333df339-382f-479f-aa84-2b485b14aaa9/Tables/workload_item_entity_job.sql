CREATE TABLE [333df339-382f-479f-aa84-2b485b14aaa9].[workload_item_entity_job] (
    [id]                   INT           IDENTITY (1, 1) NOT NULL,
    [jobId]                VARCHAR (255) NOT NULL,
    [workloadItemEntityId] INT           NOT NULL,
    [startTime]            INT           NULL,
    [endTime]              INT           NULL,
    [errorCode]            VARCHAR (255) NULL,
    [errorMsg]             VARCHAR (MAX) NULL,
    [jobMeta]              VARCHAR (MAX) NULL,
    [type]                 INT           NOT NULL,
    [status]               INT           CONSTRAINT [DF_ba53f465f742ca38a96d480aca1] DEFAULT ((10)) NOT NULL,
    [createdBy]            VARCHAR (128) NOT NULL,
    [updatedBy]            VARCHAR (128) NOT NULL,
    [createdAt]            INT           NOT NULL,
    [updatedAt]            INT           NOT NULL,
    CONSTRAINT [PK_9afdb9ed0d61dae57ad9fffbfcc] PRIMARY KEY CLUSTERED ([id] ASC)
);


GO


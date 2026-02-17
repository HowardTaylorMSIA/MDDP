CREATE TABLE [Gold].[Customer] (

	[CustomerID]            int           NOT NULL,
	[CustomerName]          varchar(100)  NULL,
	[CustomerCategoryID]    int           NULL,
	[BuyingGroupID]         int           NULL,
	[BuyingGroupName]       varchar(50)   NULL,
	[CreditLimit]           decimal(10,2) NULL,
	[IsOnCreditHold]        bit           NULL,
	[PaymentDays]           int           NULL,
	[DeliveryCityID]        int           NULL,
	[DeliveryCity]          varchar(50)   NULL,
	[DeliveryStateProvince] varchar(50)   NULL,
	[DeliveryPostalCode]    varchar(10)   NULL,
	[DeliveryCountry]       varchar(60)   NULL,
	[Region]                varchar(30)   NULL,
	[Subregion]             varchar(30)   NULL,
	[Continent]             varchar(30)   NULL,
	[SalesTerritory]        varchar(50)   NULL,
	[AreaCode]              varchar(3)    NULL,
	[YearsCustomer]         int           NULL
);
CREATE TABLE [Gold].[Customer] (

	[YearsCustomer] int NULL, 
	[BuyingGroupID] int NULL, 
	[BuyingGroupName] varchar(50) NULL, 
	[CreditLimit] decimal(10,2) NULL, 
	[CustomerCategoryID] int NULL, 
	[CustomerID] int NULL, 
	[CustomerName] varchar(100) NULL, 
	[DeliveryCityID] int NULL, 
	[DeliveryCity] varchar(50) NULL, 
	[DeliveryStateProvince] varchar(50) NULL, 
	[DeliveryCountry] varchar(60) NULL, 
	[Region] varchar(30) NULL, 
	[Subregion] varchar(30) NULL, 
	[Continent] varchar(30) NULL, 
	[SalesTerritory] varchar(50) NULL, 
	[DeliveryPostalCode] varchar(10) NULL, 
	[IsOnCreditHold] bit NULL, 
	[PaymentDays] int NULL, 
	[AreaCode] varchar(3) NULL
);
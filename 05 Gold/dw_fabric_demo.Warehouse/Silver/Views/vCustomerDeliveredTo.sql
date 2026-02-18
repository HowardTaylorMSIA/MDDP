-- Auto Generated (Do not modify) 44C26AAA6043E058AD52C9DD040E03E61F1B52AC6D3D0D28789E415F2C93EBAB



CREATE       VIEW [Silver].[vCustomerDeliveredTo] AS (SELECT DATEDIFF(yy,[AccountOpenedDate], GETDATE()) as YearsCustomer
             ,C.[BuyingGroupID]
            ,isnull([BuyingGroupName],'Undefined') as BuyingGroupName
            ,[CreditLimit]
            ,[CustomerCategoryID]
            ,[CustomerID]
            ,[CustomerName]
            ,[DeliveryCityID]
            ,[CityName] as DeliveryCity
            ,[StateProvinceName] as DeliveryStateProvince
            ,CountryName as DeliveryCountry
            ,Region
            ,Subregion
            ,Continent
            ,[SalesTerritory]
            ,[DeliveryPostalCode]
            ,[IsOnCreditHold]
            ,[PaymentDays]
            ,SUBSTRING([PhoneNumber],2,3) as AreaCode
FROM [lh_fabric_demo].[dbo].[Customers] C
left outer join [lh_fabric_demo].[dbo].[BuyingGroups] BG
on C.BuyingGroupID = BG.BuyingGroupID
inner join [lh_fabric_demo].[dbo].[Cities] CI
on C.DeliveryCityID = CI.[CityID]
inner join [lh_fabric_demo].[dbo].[StateProvinces] S
on CI.StateProvinceID = S.StateProvinceID
inner join [lh_fabric_demo].[dbo].Countries CO 
on S.CountryID = CO.CountryID)
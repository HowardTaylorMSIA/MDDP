-- Auto Generated (Do not modify) 754DF150B679FA9E3B081FA7CC0A868222D15D8D9E65A43C84BC3159D51FF0EA



CREATE     VIEW [Silver].[vCalendar] AS (SELECT [date] as Date
            ,[daynum] as DayNum
            ,[dayofweekname] as DayOfWeek
            ,[dayofweeknum] as DayOfWeekNum
            ,[monthname] as Month
            ,[monthnum] as MonthNum
            ,[quartername] as Quarter
            ,[quarternum] as QuarterNum
            ,[year] as Year
FROM [lh_fabric_demo].[dbo].[calendar])
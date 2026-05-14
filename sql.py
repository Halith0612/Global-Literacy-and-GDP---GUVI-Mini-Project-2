"""# **SQL Connection and Pusing**"""

pip install mysql-connector-python

import mysql.connector

conn = mysql.connector.connect(
    host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user = "3fXqCw6nxxduoS8.root",
    password = "u2dctQHUVuOXcZhS",
    port = 4000
)

gl = conn.cursor()

gl.execute("DROP DATABASE IF EXISTS Global_Literacy")
conn.commit()

gl.execute("CREATE DATABASE Global_Literacy")
conn.commit()

gl.execute("show databases")
gl.fetchall()

gl.execute("use Global_Literacy")

gl.execute("""CREATE TABLE literacy_rates(
              Country VARCHAR(100),
              Code CHAR(10),
              Year INT,
              Adult FLOAT,
              Male FLOAT,
              Female FLOAT,
              Region VARCHAR(50),
              Population FLOAT,
              Literacy_gap FLOAT,
              Total_Youth FLOAT,
              Avg_Youth_Literacy FLOAT,

              PRIMARY KEY (Country, Year)
              )""")

conn.commit()

gl.execute("""CREATE TABLE illiteracy_population(
              Country VARCHAR(100),
              Code CHAR(10),
              Year INT,
              Illiteracy_rate FLOAT,
              Literacy_rate FLOAT,
              Population FLOAT,
              Illiteracy_Population FLOAT,

              PRIMARY KEY (Country, Year),

              FOREIGN KEY (Country, Year)
              REFERENCES literacy_rates(Country, Year)
              )""")

conn.commit()

gl.execute("""CREATE TABLE gdp_schooling(
              Country VARCHAR(100),
              Code CHAR(10),
              Year INT,
              Region VARCHAR(50),
              GDP FLOAT,
              Literacy FLOAT,
              Avg_yrs_schooling FLOAT,
              Population FLOAT,
              GDP_per_Schooling FLOAT,
              Education_Index FLOAT,
              Growth_Rate FLOAT,

              PRIMARY KEY (Country, Year)
              )""")

conn.commit()

gl.execute("show tables")
gl.fetchall()

"""**Pushing DaraFrame to SQL**"""

pip install pandas sqlalchemy mysql-connector-python

from sqlalchemy import create_engine

engine = create_engine("mysql+mysqlconnector://3fXqCw6nxxduoS8.root:u2dctQHUVuOXcZhS@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/Global_Literacy")

df_literacy.to_sql("literacy_rates", con=engine, if_exists="append", index=False)

df_illiteracy.to_sql("illiteracy_population", con=engine, if_exists="append", index=False)

df_gdp_schooling.to_sql("gdp_schooling", con=engine, if_exists="append", index=False)

"""# SQL Queries"""

engine = create_engine("mysql+mysqlconnector://3fXqCw6nxxduoS8.root:u2dctQHUVuOXcZhS@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/Global_Literacy")

"""**literacy_rates**"""

# 1. Get top 5 countries with highest adult literacy in 2020.

top_5_countries = pd.read_sql ("""SELECT Country, MAX(Adult) AS Top_5_Countries
FROM literacy_rates WHERE Year = 2020
AND Adult IS NOT NULL
GROUP BY Country
ORDER BY Top_5_Countries DESC
LIMIT 6;""", engine)

top_5_countries

# 2. Find countries where female youth literacy < 80%.

female_literacy = pd.read_sql ("""SELECT Country, Female
FROM literacy_rates
WHERE Female < 80;""", engine)

female_literacy

# 3. Average adult literacy per continent (owid region).

avg_adult_literacy = pd.read_sql ("""SELECT Region, AVG(Adult) AS Avg_Adult_Literacy
FROM literacy_rates
GROUP BY Region;""", engine)

avg_adult_literacy

"""**illiteracy_population**"""

# 4. Countries with illiteracy % > 20% in 2000.

countries_lower_illiteracy = pd.read_sql ("""SELECT Country, Year, Illiteracy_rate
FROM illiteracy_population
WHERE Year = 2000 AND Illiteracy_rate > 20
ORDER BY Illiteracy_rate ASC;""", engine)

countries_lower_illiteracy

# 5. Trend of illiteracy % for India (2000–2020).

india_illiteracy = pd.read_sql ("""SELECT Year, Illiteracy_rate
FROM illiteracy_population
WHERE Country = 'India'
AND Year BETWEEN 2000 AND 2020;""", engine)

india_illiteracy

# 6. Top 10 countries with largest illiterate population in the last year.

top_10_illiterate = pd.read_sql ("""SELECT Country, MAX(Illiteracy_Population) AS Illiterate
FROM illiteracy_population
WHERE Year = 2023
AND Illiteracy_Population IS NOT NULL
GROUP BY Country
ORDER BY IlliTerate DESC
LIMIT 11;""", engine)

top_10_illiterate

"""**gdp_schooling**"""

# 7. Find countries with avg_years_schooling > 7 and gdp_per_capita < 5000.

avg_schooling_gdp = pd.read_sql (""" SELECT Country, Avg_yrs_schooling, GDP
FROM gdp_schooling
WHERE Avg_yrs_schooling > 7 AND GDP < 5000
AND Avg_yrs_schooling is NOT NULL
AND GDP is NOT NULL;""", engine)

avg_schooling_gdp

# 8. Rank countries by GDP per schooling for the year 2020.

rank_gdp_schooling = pd.read_sql (""" SELECT Country, GDP_per_Schooling
FROM gdp_schooling
WHERE Year = 2020
AND GDP_per_Schooling IS NOT NULL
ORDER BY GDP_per_Schooling DESC;""", engine)

rank_gdp_schooling

# 9. Find global average schooling years per year.

global_avg_schooling = pd.read_sql (""" SELECT Year, AVG(Avg_yrs_schooling) AS Avg_Schooling
FROM gdp_schooling
WHERE Avg_yrs_schooling IS NOT NULL
GROUP BY Year
ORDER BY Year ASC;""", engine)

global_avg_schooling

"""**Join Queries**"""

# 10. List top 10 countries in 2020 with highest GDP per capita but lowest average years of schooling(less than 6).

top_10_gdp_schooling = pd.read_sql (""" SELECT Country, GDP_per_Schooling, Avg_yrs_schooling
FROM gdp_schooling
WHERE Year = 2020
AND Avg_yrs_schooling < 6
AND GDP_per_Schooling IS NOT NULL
ORDER BY GDP_per_Schooling DESC
LIMIT 11;""", engine)

top_10_gdp_schooling

# 11. Show countries where the illiterate population is high despite having more than 10 average years of schooling.

illiterate_schooling = pd.read_sql (""" SELECT i.Country, i.Illiteracy_Population, g.Avg_yrs_schooling, i.Year
FROM illiteracy_population i
JOIN gdp_schooling g ON i.Country = g.Country
WHERE g.Avg_yrs_schooling > 10
AND i.Illiteracy_Population IS NOT NULL
ORDER BY i.Illiteracy_Population DESC;""", engine)

illiterate_schooling

# 12. Compare literacy rates and GDP per capita growth for a selected country over the last 20 years. (country of your choice)

slt_country = pd.read_sql (""" SELECT l.Country, l.Year, l.Avg_Youth_Literacy, g.Growth_Rate
FROM literacy_rates l
JOIN gdp_schooling g ON l.Country = g.Country AND l.Year = g.Year
WHERE l.Country = 'India'
AND l.year BETWEEN 2000 AND 2023
AND l.Avg_Youth_Literacy IS NOT NULL
AND g.GDP_per_Schooling IS NOT NULL
ORDER BY l.Year ASC;""", engine)

slt_country

literacy  = pd.read_sql ("""SELECT g.Country, g.Year, g.Literacy, l.Adult
FROM gdp_schooling g
JOIN literacy_rates l ON g.Country = l.Country AND g.Year = l.Year
WHERE g.Year BETWEEN 1990 AND 2023
AND g.Country = 'Pakistan'
AND g.Literacy IS NOT NULL
AND l.Adult IS NOT NULL
ORDER BY g.Year ASC""", engine)

literacy

# 13. Show the difference between youth literacy male and female rates for countries with GDP per capita above $30,000 in 2020.

difference = pd.read_sql (""" SELECT l.Country, l.Year, l.Male, l.Female, g.GDP
FROM literacy_rates l
JOIN gdp_schooling g ON l.Country = g.Country AND l.Year = g.Year
WHERE g.Year = 2020
AND g.GDP > 30000
AND l.Male IS NOT NULL
AND l.Female IS NOT NULL
AND g.GDP IS NOT NULL
ORDER BY g.GDP DESC;""", engine)

difference

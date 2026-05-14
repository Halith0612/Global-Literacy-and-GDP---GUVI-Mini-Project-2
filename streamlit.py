!pip install streamlit pyngrok

from pyngrok import ngrok

%%writefile app.py

# importing libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import mysql.connector
from sqlalchemy import create_engine
import time

# connecting with sql
mydb = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="3fXqCw6nxxduoS8.root",
    password="u2dctQHUVuOXcZhS",
    database="Global_Literacy"
)


# load data
@st.cache_data
def load_data():
    literacy = pd.read_sql("SELECT * FROM literacy_rates", mydb)
    illiteracy = pd.read_sql("SELECT * FROM illiteracy_population", mydb)
    gdp_schooling = pd.read_sql("SELECT * FROM gdp_schooling", mydb)
    return literacy, illiteracy, gdp_schooling

literacy, illiteracy, gdp_schooling = load_data()

# main page setup
st.set_page_config(page_title="Global Literacy and GDP ", layout="wide")
st.title("🧠💰Global Literacy and GDP Dashboard")
st.subheader("Welcome to the Global Literacy Dashboard!👋")
st.markdown("""This dashboard provides insights into global literacy rates, illiteracy population, and the relationship between GDP and schooling years.
Use the sidebar to navigate through different sections.""")

# side bar
st.sidebar.title("Menu")
page = st.sidebar.selectbox(
    "Options",
    [ "SQL Query Executor", "EDA Visualizations", "Country Profile Page"])

#page 1: sql query page
if page == "SQL Query Executor":
  st.title("SQL Query Executor")

  queries = {
      "Literacy Rates and Trends":{
          "Top 5 Countries with Highest Adult Literacy in 2020":{
              "query":
              """SELECT Country, MAX(Adult) AS Highest_Adult FROM literacy_rates
              WHERE Year = 2020 AND Adult IS NOT NULL
              GROUP BY Country ORDER BY Highest_Adult DESC LIMIT 6;""",

              "chart": "bar",
              "x": "Country",
              "y": "Highest_Adult"
              },

          "Countries where Female Youth Literacy were < 80pct":{
              "query":
              """SELECT Country, Female FROM literacy_rates WHERE Female < 80;""",

              "chart": "bar",
              "x": "Country",
              "y": "Female"
              },

          "Average Adult Literacy per Continent":{
              "query":
              """SELECT Region, AVG(Adult) AS Avg_Adult_Literacy FROM literacy_rates GROUP BY Region;""",
              "chart": "pie",
              "x": "Region",
              "y": "Avg_Adult_Literacy"
              }
          },

      "Illiteracy Population Analysis": {
          "Countries with illiteracy rate > 20pct in 2000":{
              "query":
              """SELECT Country, Year, Illiteracy_rate FROM illiteracy_population
              WHERE Year = 2000 AND Illiteracy_rate > 20 ORDER BY Illiteracy_rate ASC;""",

              "chart": "bar",
              "x": "Country",
              "y": "Illiteracy_rate"
              },

          "Trend of illiteracy rate for India (2000 to 2020)": {
              "query":
              """SELECT Year, Illiteracy_rate FROM illiteracy_population WHERE Country = 'India' AND Year BETWEEN 2000 AND 2020;""",
              "chart": "line",
              "x": "Year",
              "y": "Illiteracy_rate"
              },
          "Top 10 countries with largest illiterate population in the last year": {
              "query":
              """SELECT Country, MAX(Illiteracy_Population) AS Illiterate FROM illiteracy_population WHERE Year = 2023
              AND Illiteracy_Population IS NOT NULL GROUP BY Country ORDER BY Illiterate DESC LIMIT 10;""",

              "chart": "bar",
              "x": "Country",
              "y": "Illiterate"
              }
          },

      "GDP and Schooling Analysis": {
          "Countries with avg_years_schooling > 7 and gdp_per_capita < 5000":{
              "query":
              """SELECT Country, Avg_yrs_schooling, GDP FROM gdp_schooling
              WHERE Avg_yrs_schooling > 7 AND GDP < 5000 AND Avg_yrs_schooling is NOT NULL AND GDP is NOT NULL;""",

              "chart": "scatter",
              "x": "Avg_yrs_schooling",
              "y": "GDP"
              },

          "Ranking countries by GDP per schooling for the year 2020":{
              "query": """SELECT Country, GDP_per_Schooling FROM gdp_schooling
              WHERE Year = 2020 AND GDP_per_Schooling IS NOT NULL ORDER BY GDP_per_Schooling DESC;""",

              "chart": "scatter",
              "x": "Country",
              "y": "GDP_per_Schooling"
              },

          "Find global average schooling years per year":{
              "query": """SELECT Year, AVG(Avg_yrs_schooling) AS Avg_Schooling FROM gdp_schooling
              WHERE Avg_yrs_schooling IS NOT NULL GROUP BY Year ORDER BY Year ASC;""",

              "chart": "line",
              "x": "Year",
              "y": "Avg_Schooling"
              }
      },

      "Additional Queries": {
          "Top 10 countries in 2020 with highest GDP per capita but lowest average years of schooling(less than 6)" : {
              "query": """SELECT Country, GDP_per_Schooling, Avg_yrs_schooling FROM gdp_schooling WHERE Year = 2020
              AND Avg_yrs_schooling < 6 AND GDP_per_Schooling IS NOT NULL ORDER BY GDP_per_Schooling DESC LIMIT 11;""",

              "chart": "bar",
              "x": "Country",
              "y": "GDP_per_Schooling"
              },

          "Countries where the illiterate population is high despite having more than 10 average years of schooling" :{
              "query": """SELECT i.Country, i.Illiteracy_Population, g.Avg_yrs_schooling, i.Year FROM illiteracy_population i
              JOIN gdp_schooling g ON i.Country = g.Country WHERE g.Avg_yrs_schooling > 10 AND i.Illiteracy_Population IS NOT NULL
              ORDER BY i.Illiteracy_Population DESC;""",

              "chart": "scatter",
              "x": "Avg_yrs_schooling",
              "y": "Illiteracy_Population"
              },

          "Compare literacy rates and GDP per capita growth for India" :{
              "query": """SELECT l.Country, l.Year, l.Avg_Youth_Literacy, g.Growth_Rate FROM literacy_rates l JOIN gdp_schooling g ON l.Country = g.Country
              AND l.Year = g.Year WHERE l.Country = 'India' AND l.year BETWEEN 2000 AND 2023 AND l.Avg_Youth_Literacy IS NOT NULL
              AND g.GDP_per_Schooling IS NOT NULL ORDER BY l.Year ASC;""",

              "chart": "line",
              "x": "Year",
              "y": "Growth_Rate"
              },
          "Countries with high GDP and Difference in Literacy(Male, Female)" : {
              "query": """SELECT l.Country, l.Year, l.Male, l.Female, g.GDP FROM literacy_rates l JOIN gdp_schooling g ON l.Country = g.Country
              AND l.Year = g.Year WHERE g.Year = 2020 AND g.GDP > 30000 AND l.Male IS NOT NULL AND l.Female IS NOT NULL
              AND g.GDP IS NOT NULL ORDER BY g.GDP DESC;""",
              "chart": "grouped_bar",
              "x": "Country",
              "y1": "Male",
              "y2": "Female"
              }
          }
      }

  category = st.selectbox("Select Category", list(queries.keys()))
  query_name = st.selectbox("Select Query", list(queries[category].keys()))

  if st.button("Run Query"):
    with st.spinner("Running query..."):
      time.sleep(2)
    query_info = queries[category][query_name]
    query = query_info["query"]

    result = pd.read_sql(query, mydb)

    st.dataframe(result)

    st.subheader("📊 Query Visualization")
    chart_type = query_info["chart"]
    x_col = query_info["x"]
    y_col = query_info.get("y")

    # BAR
    if chart_type == "bar":
      fig = px.bar(result,
                   x=x_col,
                   y=y_col,
                   text_auto=True,
                   color=y_col
                   )

    elif chart_type == "line":
      fig = px.line(result,
                    x=x_col,
                    y=y_col,
                    markers=True)

    elif chart_type == "pie":
      fig = px.pie(result,
                   names=x_col,
                   values=y_col)

    elif chart_type == "scatter":
      fig = px.scatter(result,
                       x=x_col,
                       y=y_col)

    elif chart_type == "grouped_bar":
      fig = px.bar(result,
                   x=x_col,
                   y=[query_info["y1"], query_info["y2"]],
                   barmode="group"
                   )

    st.plotly_chart(fig, use_container_width=True)


# page 2:
elif page == "EDA Visualizations":

    st.title("📊 EDA Visualizations")

    eda_options = [
        "Adult & Youth Literacy Rate Over Years",

        "Region wise Male and Female Literacy Rate",

        "Adult Literacy during covid (2020 to 2023)",

        "Illiteracy Rate comparision betweeen selected countries over years",

        "Illiterates vs Literates trend over Years",

        "GDP per Avg Schooling",

        "Highest GDP countries literacy rate TOP 5 only",

        "Literacy Growth Rate over year - India.",

        "GDP Distribution Boxplot",

        "Correlation of Population and Literacy"
    ]

    eda_name = st.selectbox("Select Category",eda_options)

    def show_chart(fig):

        st.plotly_chart( fig, use_container_width=True)

    # 1
    if eda_name == "Adult & Youth Literacy Rate Over Years":
      adult_literacy = literacy.groupby("Year")["Adult"].mean()
      youth_literacy = literacy.groupby("Year")["Total_Youth"].mean()

      fig, ax = plt.subplots(figsize=(15, 8))

      ax.plot(youth_literacy.index, youth_literacy.values, label="Youth")
      ax.plot(adult_literacy.index, adult_literacy.values, label="Adult")

      ax.set_title("Avg Literacy Rate Over Years of Adult & Youth")
      ax.set_xlabel("Year")
      ax.set_ylabel("Literacy Rate")

      ax.legend()
      ax.grid(alpha=0.5)

      show_chart(fig)

    # 2
    elif eda_name == "Region wise Male and Female Literacy Rate":
      r_male_literacy = literacy.groupby("Region")["Male"].mean()
      r_female_literacy = literacy.groupby("Region")["Female"].mean()

      fig, ax = plt.subplots(figsize=(15,8))
      ax.plot(r_male_literacy.index, r_male_literacy.values, marker="o")
      ax.plot(r_female_literacy.index, r_female_literacy.values, marker="o")
      ax.set_title("Region Wise Trend")
      ax.set_xlabel("Region")
      ax.set_ylabel("Total_Youth")
      ax.grid(alpha=0.5)
      ax.legend(["Male", "Female"])

      st.pyplot(fig)

    # 3
    elif eda_name == "Adult Literacy during covid (2020 to 2023)":
      covid_year = literacy[(literacy["Year"] >= 2020) & (literacy["Year"] <= 2023)]
      adult_literacy = covid_year.groupby("Year", as_index=False)["Adult"].mean().round()

      fig, ax = plt.subplots(figsize=(15,8))

      sns.barplot(data=adult_literacy, x="Year", y="Adult", palette="dark", ax=ax)

      ax.set_title("Adult Literacy During COVID (2020 to 2023)")
      ax.set_xlabel("Year")
      ax.set_ylabel("Adult Literacy")
      ax.legend(loc="upper center")

      st.pyplot(fig)

    # 4
    elif eda_name == "Illiteracy Rate comparision betweeen selected countries over years":
        countries = ["Bangladesh", "China", "India", "Nepal", "Pakistan"]

        com_countries = illiteracy[illiteracy["Country"].isin(countries)]

        fig, ax = plt.subplots(figsize=(15, 8))

        sns.barplot(data=com_countries, x="Year", y="Illiteracy_rate", palette="magma", ax=ax)

        ax.set_title("Illiteracy Rate of Five Countries")
        ax.set_xlabel("Year")
        ax.set_ylabel("Illiteracy Rate")

        ax.legend(loc="upper right")
        ax.grid(False)

        st.pyplot(fig)

    # 5
    elif eda_name == "Illiterates vs Literates trend over Years":

        data = illiteracy.groupby("Year", as_index=False)[["Illiteracy_rate", "Literacy_rate"]].mean()

        fig = px.line(data, x="Year", y=["Illiteracy_rate", "Literacy_rate"], markers=True)

        show_chart(fig)

    # 6
    elif eda_name == "GDP per Avg Schooling":

        fig = px.scatter(gdp_schooling, x="Avg_yrs_schooling", y="GDP", color="Region")

        show_chart(fig)

    # 7
    elif eda_name == "GDP Distribution Boxplot":

        fig = px.box(gdp_schooling, x="Year", y="GDP")

        show_chart(fig)

    # 8
    elif eda_name == "Correlation of Population and Literacy":
      data = gdp_schooling[(gdp_schooling["Year"] >= 2020) & (gdp_schooling["Year"] <= 2023)]
      df = data.groupby("Year", as_index=False).agg({"Population": "mean", "Literacy": "mean"})
      df["Population_Million"] = df["Population"] / 1_000_000

      fig = make_subplots(specs=[[{"secondary_y": True}]])

      # Population bar
      fig.add_trace(go.Bar(x=df["Year"],y=df["Population_Million"],name="Population (Million)"),secondary_y=False)

      # Literacy line (IMPORTANT FIX HERE)
      fig.add_trace(go.Scatter(x=df["Year"],y=df["Literacy"],mode="lines+markers",name="Literacy Rate (%)"),secondary_y=True)

      fig.update_layout(title="Population Growth vs Literacy Growth (2020–2023)", width=900, height=600, template="plotly_white")

      fig.update_xaxes(title_text="Year")

      fig.update_yaxes(title_text="Population (Millions)", secondary_y=False)

      fig.update_yaxes(title_text="Literacy Rate (%)", secondary_y=True, range=[0, 100])

      show_chart(fig)

    # 9
    elif eda_name == "Highest GDP countries literacy rate TOP 5 only":
      data = gdp_schooling.groupby( "Country", as_index=False )[["GDP", "Literacy"]].mean()

      #top 5
      data = data.sort_values( by="GDP", ascending=False ).head(5)

      fig = px.bar(data, x="Country", y=["GDP", "Literacy"], barmode="group")

      show_chart(fig)

    # 10
    elif eda_name == "Literacy Growth Rate over year - India.":

        data = literacy[
            literacy["Country"] == "India"][["Year", "Adult", "Avg_Youth_Literacy"]]

        fig = px.line(data, x="Year", y=["Adult", "Avg_Youth_Literacy"], markers=True)

        show_chart(fig)

# page 3
elif page == "Country Profile Page":

    st.title("🌍 Country Profile Page")
    country = st.selectbox("Select Country", sorted(literacy["Country"].unique()))
    row1_col1, row1_col2 = st.columns(2)
    row3_col1, row3_col2 = st.columns(2)

    # filter data
    literacy_data = literacy[literacy["Country"] == country]

    illiteracy_data = illiteracy[illiteracy["Country"] == country]

    gdp_data = gdp_schooling[gdp_schooling["Country"] == country]

    # literacy trend
    with row1_col1:
      st.subheader("📘 Literacy Trends")
      fig1 = px.line( literacy_data, x="Year", y=["Adult", "Avg_Youth_Literacy"], markers=True, title=f"{country} Literacy Trends")

      st.plotly_chart( fig1, use_container_width=True )

    # illiteracy trend
    with row1_col2:
      st.subheader("📉 Illiteracy Trend")

      fig5 = px.line(illiteracy_data, x="Year", y="Illiteracy_rate", markers=True, title=f"{country} Illiteracy Trend")

      st.plotly_chart(fig5,use_container_width=True)

    # schooling trend
    st.subheader("🎓 Average Schooling Years")

    fig3 = px.line(gdp_data, x="Year", y="Avg_yrs_schooling", markers=True, title=f"{country} Schooling Trend")

    st.plotly_chart(fig3,use_container_width=True)

    # population trend
    with row3_col1:
      st.subheader("👨‍👩‍👧 Population Trend")

      fig4 = px.bar(gdp_data, x="Year", y="Population", title=f"{country} Population")

      st.plotly_chart(fig4, use_container_width=True)

    # gdp trend
    with row3_col2:
      st.subheader("💰 GDP Trend")
      fig2 = px.line(gdp_data, x="Year", y="GDP", markers=True, title=f"{country} GDP Over Years")

      st.plotly_chart(fig2, use_container_width=True)

ngrok.set_auth_token("3DfZN4RcDTbGEZxx7cfRRAi045e_5xLeR6pKV57CM634VJbgt")
!streamlit run app.py &>/content/logs.txt &

public_url = ngrok.connect(8501)
print(public_url)

import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Loading preprocessed dataset
df = pd.read_csv(os.getcwd() + "/dataset.csv")

# Streamlit setup
st.title("Football Transfer History Dashboard")
st.header("Statistics on every football player transfer from 1992 to 2021, in the top 9 biggest leagues")
st.sidebar.header("Filters")

# Filters
club_filter = st.sidebar.multiselect("Select Clubs", df['club_name'].unique())
transfer_movement_filter = st.sidebar.selectbox("Select Transfer Movement", ['Any', 'Inbound', 'Outbound'])
min_year_filter = st.sidebar.selectbox("Select Min Year", df['year'].unique(), index=0)
max_year_filter = st.sidebar.selectbox("Select Max Year", df['year'].unique(), index=len(df['year'].unique()) - 1)
league_filter = st.sidebar.multiselect("Select Leagues", df['league_name'].unique())
position_filter = st.sidebar.multiselect("Select Positions", df['position'].unique())

# Filters application
if club_filter:
    df = df[df['club_name'].isin(club_filter)]
if transfer_movement_filter != 'Any':
    df = df[df['transfer_movement'] == transfer_movement_filter]
if position_filter:
    df = df[df['position'].isin(position_filter)]
if min_year_filter:
    df = df[df['year'] >= min_year_filter]
if max_year_filter:
    df = df[df['year'] <= max_year_filter]
if league_filter:
    df = df[df['league_name'].isin(league_filter)]

# chart 1: most expensive transfers per season
df_chart1 = df.groupby('season')['fee_cleaned'].max().reset_index()
st.write(
    px.line(
        df_chart1,
        x='season',
        y='fee_cleaned',
        title="Most Expensive Transfer per Season")
    .update_xaxes(title_text="Season")
    .update_yaxes(title_text="Transfer Fee")
)
st.markdown("The above chart displays the amount of the highest transfer fee per season.")

# chart 2: number of transfers per season
df_chart2 = df.groupby('season')['player_name'].count().reset_index()
df_chart2 = df_chart2.rename(columns={'player_name': 'Number of Transfers'})
st.write(
    px.line(
        df_chart2,
        x='season',
        y='Number of Transfers',
        title="Number of Transfers per Season"
    )
    .update_xaxes(title_text="Season")
)
st.markdown("The above chart displays the number of players that were signed/released per season. Recommended to use club filters to see which clubs signed/released the most players.")

# chart 3: scatter plot, x=season, y=fee, color=league
min_fee = st.slider("Select minimum transfer fee for below chart", min_value=0.0, max_value=df['fee_cleaned'].max(), value=0.0)
df_chart3 = df[df['fee_cleaned'] >= min_fee]
st.write(
    px.scatter(
        df_chart3,
        x='season',
        y='fee_cleaned',
        color='league_name',
        title='Transfers per Season, colored by League',
        labels={
            'season': 'Season',
            'fee_cleaned': 'Transfer Fee',
            'league_name': 'League' 
        }
    )
)
st.markdown("The above chart represents each transfer per season, color coded by leagues. Slider above to filter out by minimum transfer fees.")

# chart 4: pivot table, club_name, total "in" transfer fee sum, total "out" transfer fee sum, number of "in" transfers, number of "out" transfers, average transfer fee
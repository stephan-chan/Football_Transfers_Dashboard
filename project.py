import os
import pandas as pd
import streamlit as st
import plotly.express as px
import base64


# Dataset columns:
#    club_name : name of the club
#    player_name : name of the player
#    age : age at transfer
#    position : position the player plays
#    club_involved_name : other club involved in transfer
#    fee : type of contract (price, fee, loan, etc)
#    transfer_movement : Inbound (club_involved_name -> club_name) or Outbound (club_name -> club_involved_name)
#    transfer_period : Summer or Winter mercato
#    fee_cleaned : price of transfer - 0 if free/loan
#    league_name : league in which club_name belongs
#    year : year of transfer
#    season : season of the transfer
#    season_start : season start year
#    season_end : season end year

# Loading preprocessed dataset
df = pd.read_csv(os.getcwd() + "/dataset.csv")

# Streamlit setup
st.title("Football Transfer History Dashboard")
st.header("Statistics on every football player transfer from 1992 to 2021, in the top 9 biggest leagues")
st.sidebar.header("Universal Filters")
st.subheader("Hypothesis: The transfer value of a player is determined by a combination of numerous factors including the player's age, the clubs involved, his position, of course general perfomance, etc..")
st.subheader("After a certain age, a player starts losing value as he ages.")

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
slider = st.slider("Select transfer fee range for below chart", min_value=0.0, max_value=df['fee_cleaned'].max(), value=(0.0, 222.0))
df_chart3 = df[df['fee_cleaned'] >= slider[0]]
df_chart3 = df_chart3[df_chart3['fee_cleaned'] <= slider[1]]
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

# chart 4: pie chart of transfers distribution per league

age_slider = st.slider("Select age range for below chart", min_value=0, max_value=50, value=(0,50))
df_chart4 = df[df['age'] >= age_slider[0]]
df_chart4 = df_chart4[df_chart4['age'] <= age_slider[1]]
df_chart4 = df_chart4['league_name'].value_counts().reset_index()
st.write(
    px.pie(
        df_chart4,
        values='count',
        names='league_name',
        title='Distribution of Transfers per League'
    )
)
st.markdown("The above chart displays the distribution of transfers per league. Recommended to use the transfer movement filter and age slider to see which leagues are interesting for young prospects and which leagues are interesting for more \"experienced\" players.")

# chart 5: bar chart, top 5 highest spending leagues
df_chart5 = df['transfer_movement'] = 'Inbound'
df_chart5 = df.groupby('league_name')['fee_cleaned'].sum().reset_index()
df_chart5 = df_chart5.sort_values(by='fee_cleaned', ascending=False)
st.write(
    px.bar(
        df_chart5,
        x='league_name',
        y='fee_cleaned',
        title='Highest Spending Leagues on Football Transfers',
        labels={
            'season': 'Season',
            'fee_cleaned': 'Total Spent (Millions)',
            'league_name': 'League'
        }
    )
    .update_layout(xaxis_categoryorder='total descending')
)
st.markdown("The above chart shows the highest spending leagues.")

# chart 6: bar chart, top 5 highest spending teams(clubs) colored by league
df_chart6 = df['transfer_movement'] = 'Inbound'
df_chart6 = df.groupby(['club_name', 'league_name'])['fee_cleaned'].sum().reset_index()
df_chart6 = df_chart6.sort_values(by='fee_cleaned', ascending=False)
st.write(
    px.bar(
        df_chart6,
        x='club_name',
        y='fee_cleaned',
        color='league_name',
        title='Highest Spending Teams on Football Transfers',
        labels={
            'season': 'Season',
            'fee_cleaned': 'Total Spent (Millions)',
            'league_name': 'League',
            'club_name': 'Club'
        }
    )
    .update_layout(xaxis_categoryorder='total descending')
)
st.markdown("The above chart shows the highest spending teams in all the leagues. Filters can be applied to analyze each league in detail.")

# chart 7: scatter plot, relationship between player age and transfer fee.

st.write(
    px.scatter(
        df,
        x='age',
        y='fee_cleaned',
        title='Relationship between age and transfer fee',
        color='league_name',
        hover_data=['player_name', 'club_name', 'league_name'],
        range_x=(0, 50)
    )
)
st.markdown("The above chart shows the relationship between age and transfer fee.")

# chart 8: heatmap of most transfered positions

positions_coor = {
    'position': ['Defensive Midfield', 'Left Midfield', 'Centre-Forward', 'Right-Back', 'Goalkeeper', 'Attacking Midfield', 'Left-Back', 'Central Midfield', 'Left Winger', 'Centre-Back', 'Right Midfield', 'Right Winger'],
    'x': [2, 1, 2, 3, 2, 2, 1, 2, 1, 2, 3, 3],
    'y': [5, 7, 11, 3, 1, 9, 3, 7, 11, 3, 7, 11]
}   
pos_df = pd.DataFrame(positions_coor)

df_chart8 = df['position'].value_counts().reset_index()

defence_count = df_chart8.loc[df_chart8['position'] == 'defence', 'count'].sum()
midfield_count = df_chart8.loc[df_chart8['position'] == 'midfield', 'count'].sum()
attack_count = df_chart8.loc[df_chart8['position'] == 'attack', 'count'].sum()
sstriker_count = df_chart8.loc[df_chart8['position'] == 'Second Striker', 'count'].sum()
sweeper_count = df_chart8.loc[df_chart8['position'] == 'Sweeper', 'count'].sum()

df_chart8.loc[df_chart8[df_chart8['position'] == 'Centre-Back'].index, 'count'] += defence_count + sweeper_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Left-Back'].index, 'count'] += defence_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Right-Back'].index, 'count'] += defence_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Central Midfield'].index, 'count'] += midfield_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Left Midfield'].index, 'count'] += midfield_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Right Midfield'].index, 'count'] += midfield_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Centre-Forward'].index, 'count'] += attack_count + sstriker_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Left Winger'].index, 'count'] += attack_count
df_chart8.loc[df_chart8[df_chart8['position'] == 'Right Winger'].index, 'count'] += attack_count

df_chart8 = df_chart8[~df_chart8['position'].isin(['defence', 'midfield', 'attack', 'Second Striker', 'Sweeper'])]

df_chart8 = pd.merge(df_chart8, pos_df, on='position', how='left')

football_pitch_image = base64.b64encode(open(os.getcwd() + "/football_pitch.png", 'rb').read())

st.write(
    px.density_heatmap(
        df_chart8,
        x='x',
        y='y',
        z='count',
        nbinsy=6,
        color_continuous_scale=['#008000', '#FFFF00', '#FF0000'],
        title='Most Transfered Positions',
        labels={
            'x': 'Left-Right',
            'y': 'Defence-Attack',
            'count': 'transfers'
        },
        #hover_data=['position', 'count', 'x', 'y'], # try to display the position name on the heatmap
        height=700,
        range_y=[0, 13]
    )
    .update_layout(
                images= [dict(
                    source='data:image/png;base64,{}'.format(football_pitch_image.decode()),
                    xref="paper", yref="paper",
                    x=0, y=1,
                    sizex=1, sizey=1,
                    xanchor="left",
                    yanchor="top",
                    sizing="stretch",
                    opacity=0.5,
                    layer="above")])
)

st.markdown("The above chart displays the heatmap of which positions are most transfered in function of their position on the pitch.")

# chart 9: Transfer Window Analysis - Stacked Area Chart

transfer_windows = df.groupby(['season_start', 'transfer_period']).size().reset_index(name='transfer_count')
transfer_windows_pivot = transfer_windows.pivot(index='season_start', columns='transfer_period', values='transfer_count').fillna(0)

fig_transfer_window = px.area(transfer_windows_pivot, x=transfer_windows_pivot.index, y=['summer', 'winter'],
                              title='Transfer Window Analysis', labels={'value': 'Number of Transfers', 'index': 'Year'})
fig_transfer_window.update_layout(yaxis=dict(title='Number of Transfers'))

st.write(fig_transfer_window)

st.markdown("The above chart shows the transfer window analysis of players in different period(summer and winter).")

# chart 10: stacked bar chart, showing distribution of 

p = 0
f = 0
l = 0
u = 0
for transfer in df['fee']:
    if transfer == 'loan transfer':
        l += 1
    elif transfer == 'free transfer':
        f += 1
    elif transfer == '?':
        u += 1
    else:
        p += 1

df_chart10 = {
    'type': ['free', 'loan', 'paid', 'unclear'],
    'count': [f, l, p, u]
}

st.write(
    px.pie(
        df_chart10,
        values='count',
        names='type',
        hole=0.5,
        title="Distribution of Transfer Types"
    )
)
st.markdown("The above chart displays the distribution of transfer types (loan, free, paid, unclear is when the data is skewed). Recommended to use Transfer Movement filter and as well as League/Club filter.")

# Conclusion
st.subheader("As the charts display, there is no one parameter to determine the worth of a player, it is a combination of numerous factors including age (big factor) as well as the team buying the player, position, etc. Each transfer is particular on it's own and the contribution of each possible factor varies.")
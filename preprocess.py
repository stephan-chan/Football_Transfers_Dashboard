import os
import pandas as pd

data_dir = os.getcwd() + "/raw_data"
files_list = os.listdir(data_dir)

df = pd.concat([pd.read_csv(data_dir + "/" + f) for f in files_list ], ignore_index=True)

def season_start_year(season):
    return int(season[0:4])

def season_end_year(season):
    return int(season[5:9])

df = df[df['age'] > 0]
df = df[df['age'] < 100]

df['season_start'] = df['season'].apply(season_start_year)
df['season_end'] = df['season'].apply(season_end_year)

df['season_start'] = pd.to_datetime(df['season_start'], format='%Y')
df['season_end'] = pd.to_datetime(df['season_end'], format='%Y')
df['transfer_period'] = df['transfer_period'].str.lower()

df['age'].fillna(-1, inplace=True)
df['age'] = df['age'].astype(int)

df['league_name'].replace('1 Bundesliga', 'Bundesliga', inplace=True)
df['fee'].fillna('', inplace=True)
df.loc[df['fee'].str.contains('loan', case=False), 'fee'] = 'loan transfer'
df.loc[df['fee'].str.contains('free', case=False), 'fee'] = 'free transfer'

df.loc[df['transfer_movement'].str.contains('out', case=False), 'transfer_movement'] = 'Outbound'
df.loc[df['transfer_movement'].str.contains('in', case=False), 'transfer_movement'] = 'Inbound'

df.to_csv('dataset.csv', index=False)
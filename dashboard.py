import pandas as pd
import streamlit as st
import plotly.express as px
import datetime

PREMATCH_EXPORT_LATEST_CSV = "https://raw.githubusercontent.com/foppini975/Scommesse_export/main/prematch_export.latest.csv"

def get_league_from_url(url):
    url_tail = url.replace('https://www.snai.it/sport/CALCIO/', '')
    return url_tail.split('/')[0].replace('%20', '_')

def get_text_name(row, length = 3):
    return row['home_team'][:length] + "-" + row['away_team'][:length]

@st.cache
def load_data():
    df = pd.read_csv(PREMATCH_EXPORT_LATEST_CSV)
    #df_regional.rename(columns={'data': 'data_string'}, inplace=True)
    df['league'] = df.apply (lambda row: get_league_from_url(row['prematch_url']), axis=1)
    df['hover_name'] = df['home_team'] + '-' + df['away_team']
    df['text_name'] = df.apply(lambda row: get_text_name(row), axis=1)
    df.dropna(inplace=True)
    ##df_regional.drop(columns=['data_string'], inplace=True)
    df['refreshed_on'] = df.apply (lambda row: datetime.datetime.strptime(row['refreshed_at'],"%Y-%m-%d %H:%M:%S.%f").date(), axis=1)

    for column in ('odds_1', 'odds_X', 'odds_2', '1X2 Vig',
        'odds_1X', 'odds_X2', 'odds_12', 'DC Vig',
        'odds_gol','odds_nogol','G/NG Vig',
        'odds_under_2.5', 'odds_over_2.5', 'U/O 2.5 Vig'):
        df[column] = df[column].round(2)
    return df

def main():
    df = load_data()

    st.title('Dashboard scommesse')

    st.sidebar.title('Pannello Interattivo')
    league_select = st.sidebar.radio('Seleziona la competizione:', ('SERIE_A', 'PREMIER_LEAGUE', 'LIGA',\
        'BUNDESLIGA', 'LIGUE_1', 'CHAMPIONS_LEAGUE', 'EUROPA_LEAGUE') )

    betting_select = st.sidebar.radio('Seleziona la scommessa:', ('1X2', 'Doppia Chance', 'Gol/Nogol', 'Under/Over 2.5'))
    betting_columns = {'1X2': ['odds_1', 'odds_X', 'odds_2', '1X2 Vig', '1X2 timestamp'],
                        'Doppia Chance': ['odds_1X', 'odds_X2', 'odds_12', 'DC Vig', 'DC timestamp'],
                        'Gol/Nogol': ['odds_gol', 'odds_nogol', 'G/NG Vig', 'G/NG timestamp'],
                        'Under/Over 2.5': ['odds_under_2.5', 'odds_over_2.5', 'U/O 2.5 Vig', 'U/O 2.5 timestamp']}

    one_week_back = datetime.date.today() + datetime.timedelta(days=-2)
    start_date = st.sidebar.date_input('Eventi refreshati a partire da:', one_week_back)

    show_labels = st.sidebar.checkbox('Mostra nomi squadre nel grafico')
    label_length = st.sidebar.slider('Abbreviazione nomi squadre (caratteri):', 1, 10, 3)
    df['text_name'] = df.apply(lambda row: get_text_name(row, label_length), axis=1)

    st.header(f"{league_select} {betting_select}")

    #st.table(df[df['league'] == league_select])
    df_filtered = df[(df['league'] == league_select) & (df['refreshed_on'] >= start_date)]
    st.table(df_filtered[['home_team', 'away_team', 'refreshed_on'] + betting_columns[betting_select]])

    chart = None
    if betting_select == 'Gol/Nogol':
        if show_labels:
            chart = px.scatter(df_filtered, x="odds_gol", y="odds_nogol", color="G/NG Vig", text = "text_name", hover_name="hover_name")
        else:
            chart = px.scatter(df_filtered, x="odds_gol", y="odds_nogol", color="G/NG Vig", hover_name="hover_name")
    elif betting_select == 'Under/Over 2.5':
        if show_labels:
            chart = px.scatter(df[df['league'] == league_select], x="odds_under_2.5", y="odds_over_2.5", color="U/O 2.5 Vig", text="text_name", hover_name="hover_name")
        else:
            chart = px.scatter(df[df['league'] == league_select], x="odds_under_2.5", y="odds_over_2.5", color="U/O 2.5 Vig", hover_name="hover_name")
    elif betting_select == '1X2':
        if show_labels:
            chart = px.scatter_3d(df[df['league'] == league_select], x="odds_1", y="odds_X", z="odds_2",
                color='1X2 Vig', text="text_name", hover_name='hover_name', width = 600, height = 800)
        else:
            chart = px.scatter_3d(df[df['league'] == league_select], x="odds_1", y="odds_X", z="odds_2",
                color='1X2 Vig', hover_name='hover_name', width = 600, height = 800)
    elif betting_select == 'Doppia Chance':
        if show_labels:
            chart = px.scatter_3d(df[df['league'] == league_select], x="odds_1X", y="odds_X2", z="odds_12",
                color='DC Vig', text='text_name', hover_name='hover_name', width = 600, height = 800)
        else:
            chart = px.scatter_3d(df[df['league'] == league_select], x="odds_1X", y="odds_X2", z="odds_12",
                color='DC Vig', hover_name='hover_name', width = 600, height = 800)
    st.plotly_chart(chart)



if __name__ == '__main__':
    main()
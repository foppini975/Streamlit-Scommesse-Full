import pandas as pd
import streamlit as st
import plotly.express as px
import datetime
import numpy as np
import math
import matplotlib.pyplot as plt

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
    #df['text_name'] = df.apply(lambda row: get_text_name(row), axis=1)
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
    df = load_data().copy()

    st.title('Dashboard scommesse')

    st.sidebar.title('Pannello Interattivo')
    league_select = st.sidebar.radio('Seleziona la competizione:', ('SERIE_A', 'PREMIER_LEAGUE', 'LIGA',\
        'BUNDESLIGA', 'LIGUE_1', 'CHAMPIONS_LEAGUE', 'EUROPA_LEAGUE', 'TUTTE LE COMPETIZIONI') )

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

    color_select = st.sidebar.radio("Seleziona la dimensione del colore:", ('1X2 Vig', 'DC Vig', 'U/O 2.5 Vig', 'G/NG Vig', 'odds_1', 'odds_under_2.5', 'odds_gol', 'league'))

    st.header(f"{league_select} {betting_select}")

    #st.table(df[df['league'] == league_select])
    if league_select == 'TUTTE LE COMPETIZIONI':
        df_filtered = df[df['refreshed_on'] >= start_date]
    else:
        df_filtered = df[(df['league'] == league_select) & (df['refreshed_on'] >= start_date)]
    st.table(df_filtered[['home_team', 'away_team', 'refreshed_on'] + betting_columns[betting_select]])

    chart = None
    CHART_WIDTH = 800
    CHART_HEIGHT = 800
    text = "text_name" if show_labels else None
    chart2 = None
    if betting_select == 'Gol/Nogol':
        chart = px.scatter(df_filtered, x="odds_gol", y="odds_nogol", color=color_select, text=text, hover_name="hover_name", width = CHART_WIDTH, height = CHART_HEIGHT)
    elif betting_select == 'Under/Over 2.5':
        chart = px.scatter(df_filtered, x="odds_under_2.5", y="odds_over_2.5", color=color_select, text=text, hover_name="hover_name", width = CHART_WIDTH, height = CHART_HEIGHT)
    elif betting_select == '1X2':
        chart = px.scatter_3d(df_filtered, x="odds_1", y="odds_X", z="odds_2",
            color=color_select, text=text, hover_name='hover_name', width = CHART_WIDTH, height = CHART_HEIGHT)
    elif betting_select == 'Doppia Chance':
        chart = px.scatter_3d(df_filtered, x="odds_1X", y="odds_X2", z="odds_12",
            color=color_select, text=text, hover_name='hover_name', width = CHART_WIDTH, height = CHART_HEIGHT)

    st.plotly_chart(chart)

    if betting_select in ['Gol/Nogol', 'Under/Over 2.5']:
        x_column = betting_columns[betting_select][0]
        y_column = betting_columns[betting_select][1]
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.scatter(df_filtered[x_column], df_filtered[y_column])
        #min_vig, max_vig = min(df_filtered['G/NG Vig']) / 100, max(df_filtered['G/NG Vig']) / 100
        min_x, max_x = min(df_filtered[x_column]), max(df_filtered[x_column])
        min_y, max_y = min(df_filtered[y_column]), max(df_filtered[y_column])
        x = np.linspace(min_x - .1, max_x + .1, 400)
        y = np.linspace(min_y - .1, max_y + .1, 400)
        x, y = np.meshgrid(x, y)
        for vig in [.04, .05, .06, .07, .08, .09, .1]:
            a, b, c, d, e, f = 0, 1, 0, vig-1, vig-1, 0
            ax.contour(x, y,(a*x**2 + b*x*y + c*y**2 + d*x + e*y + f), [0], colors='b', alpha=0.5, linewidths=0.5, linestyles='dashed')
        ax.set_title(league_select + ' - ' + betting_select)
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        st.pyplot(fig)

if __name__ == '__main__':
    main()
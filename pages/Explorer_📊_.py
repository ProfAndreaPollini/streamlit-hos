import streamlit as st
import numpy as np
import pandas as pd
import sqlite3 as sq
import pygwalker as pyg

import streamlit.components.v1 as components

import plotly.figure_factory as ff

@st.cache_data
def get_data_years():
    conn = sq.connect('../db.sqlite')
    c = conn.cursor()   

    c.execute("SELECT DISTINCT strftime('%Y', orario) FROM misurazioni")
    res = c.fetchall()
    conn.close()
    st.session_state['years'] = [int(r[0]) for r in res]

st.session_state['data'] = {}

@st.cache_data
def get_data(year,month,day):
    conn = sq.connect('../db.sqlite')
    c = conn.cursor()   

   

    df = pd.read_sql(f"SELECT * FROM misurazioni WHERE strftime('%Y-%m-%d',orario) = '{year}-{month:02}-{day:02}'",con=conn,parse_dates=['orario'])
    
    
    # st.session_state['data']['{year}-{month:02}'] = df
    
    conn.close()
    return df

# Configure the Streamlit page
st.set_page_config(
    page_title="Data Explorer",
    layout="wide"
)

# Add a title
st.title("Data Explorer")


get_data_years()

# st.sidebar.markdown(""" ## Filtra per anno""")
# year = st.sidebar.selectbox("Seleziona un anno", st.session_state['years'])

# # create month filter by name but with int values
# months = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
# month = st.sidebar.selectbox("Seleziona un mese", months)
# month_idx = months.index(month) + 1

# day = st.sidebar.selectbox("Seleziona un giorno", range(1,32))

# create a date filter
import datetime
selected_date = st.sidebar.date_input("Seleziona il giorno",min_value=datetime.date(min(st.session_state['years']), 1, 1))

data = get_data(selected_date.year,selected_date.month,selected_date.day)

st.header(f"Dati del {selected_date.day}/{selected_date.month}/{selected_date.year}")

st.line_chart(data,
              x="orario",
              
              y=["ntc_1", "ntc_2", "ntc_3", "ntc_4", "ntc_5", "ntc_6", "ntc_7", "ntc_8", "ntc_9", "ntc_10", "ntc_11"])


# # Generate the HTML using Pygwalker
# pyg_html = pyg.walk(st.session_state["data"], return_html=True)

# # Embed the generated HTML into the Streamlit app
# components.html(pyg_html, height=1000, scrolling=True)


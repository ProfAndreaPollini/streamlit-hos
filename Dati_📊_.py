import streamlit as st
import numpy as np
import pandas as pd
import sqlite3 as sq

import plotly.figure_factory as ff

@st.cache_data
def get_data():
    conn = sq.connect('../db.sqlite')
    c = conn.cursor()
    df = pd.read_sql('SELECT * FROM misurazioni ORDER BY orario DESC LIMIT 1000',con=conn,parse_dates=['orario'])
    
    
    st.session_state['daily_df'] = df
    
    conn.close()



get_data()

st.title('Today Data')

st.line_chart(st.session_state['daily_df'],
              x="orario",
              
              y=["ntc_1", "ntc_2", "ntc_3", "ntc_4", "ntc_5", "ntc_6", "ntc_7", "ntc_8", "ntc_9", "ntc_10", "ntc_11"])
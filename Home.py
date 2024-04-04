import streamlit as st
import numpy as np
import pandas as pd

import plotly.figure_factory as ff

from enum import Enum

class StatoValvola(Enum):
    APERTA = 1
    CHIUSA = 2
    PASSTHROUGH = 0

bg_color = {
    StatoValvola.APERTA: "green",
    StatoValvola.CHIUSA: "red",
    StatoValvola.PASSTHROUGH: "gray"
}

text_color = {
    StatoValvola.APERTA: "white",
    StatoValvola.CHIUSA: "white",
    StatoValvola.PASSTHROUGH: "black"
}

css_stato_valvola = [f"""
       span[kind="{x.name.lower()}"] {{
            color: {text_color[x]};
            background-color: {bg_color[x]};
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 20px;
            font-weight: bold;
            margin: 10px;
         
        }}  
""" for x in StatoValvola]

st.title("Magazzino del Sole")

st.markdown(""" ## Stato valvole""")

st.markdown(f"""
<style>
   {"".join(css_stato_valvola)}
</style>
""", unsafe_allow_html=True)

def get_valvola(num:int,stato: StatoValvola):
    return f"""<span kind="{stato.name.lower()}">{num}</span>"""

def get_stato_valvole():
    c = st.columns(len(st.session_state['valvole']))
    for n,valvola in enumerate(st.session_state['valvole']):
        c[n].write(get_valvola(n,valvola),unsafe_allow_html=True)
  
import sqlite3 as sq


if 'valvole' not in st.session_state:
    st.session_state['valvole'] = [StatoValvola.APERTA, StatoValvola.CHIUSA, StatoValvola.PASSTHROUGH,StatoValvola.APERTA, StatoValvola.CHIUSA,StatoValvola.APERTA, StatoValvola.CHIUSA]

if 'temperature' not in st.session_state:
    st.session_state['temperature'] = [ 100.0 * np.random.rand() for _ in range(11)]

if "t_ambiente" not in st.session_state:
    st.session_state["t_ambiente"] = 25.0

if "t_pannello_pilota" not in st.session_state:
    st.session_state["t_pannello_pilota"] = 35.0

# @st.cache_data
def update_data():
    if 'temperature' in st.session_state:
        st.session_state['temperature_old'] = st.session_state['temperature']
    else:
        st.session_state['temperature_old'] = [0 for _ in range(11)]


    if 't_ambiente' in st.session_state:
        st.session_state['t_ambiente_old'] = st.session_state['t_ambiente']
    else:
        st.session_state['t_ambiente_old'] = 0

    if 't_pannello_pilota' in st.session_state:
        st.session_state['t_pannello_pilota_old'] = st.session_state['t_pannello_pilota']
    else:
        st.session_state['t_pannello_pilota_old'] = 0
    conn = sq.connect('db.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM misurazioni ORDER BY orario DESC LIMIT 1 OFFSET 110')
    res = c.fetchone()
    st.table(res)
    st.session_state['temperature'] = res[2:13]
    
    st.session_state['t_ambiente'] = res[13]
    # st.session_state['t_ambiente_old'] = res[13]
    st.session_state['t_pannello_pilota'] = res[14]
    for n in range(7):
         st.session_state['valvole'][n] = StatoValvola(res[15+n])

    conn.commit()
    conn.close()

update_data()



get_stato_valvole()

st.sidebar.markdown(""" ## Azioni""")
if st.sidebar.button("Aggiorna valvole"):
    st.session_state['valvole'] = np.random.choice(list(StatoValvola),len(st.session_state['valvole']))
    update_data()
    
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=3,
    cols=4,
    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
              [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
              [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
    # subplot_titles=[f"Temperatura {n}" for n in range(11)]
    vertical_spacing=0.2,
    # row_heights=[0.9, 0.9, 0.9]
    horizontal_spacing=0.1

    )




for n,temp in enumerate(st.session_state['temperature']):
    f =go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = temp,

    mode = "gauge+number+delta",
    title = {'text': f"NTC{n}"},
    delta = {'reference': st.session_state['temperature_old'][n]},
    gauge = {'axis': {'range': [None, 100]},
             'steps' : [
                 {'range': [0, 30], 'color': "lightgray"},
                 {'range': [30, 70], 'color': "gray"}],
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.85, 'value': 90}})
    fig.append_trace(f,row=n//4+1,col=n%4+1)

    # fig.append_trace(f,row=row,col=col+1)


    fig.update_layout(
    grid = {'rows': 2, 'columns': 2, 'pattern': "independent"},
    
)

st.plotly_chart(fig,use_container_width=True)

## temperatura ambiente
fig_t_amb = go.Indicator(
    mode = "gauge+number",
    value = st.session_state["t_ambiente"],
    title = {'text': "Temperatura ambiente"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': st.session_state["t_ambiente_old"]},
    gauge = {'axis': {'range': [None, 50]},
             'steps' : [
                 {'range': [0, 30], 'color': "lightgray"},
                 {'range': [30, 50], 'color': "gray"}],
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 45}})

fig_t_pannello_pilota = go.Indicator(
    mode = "gauge+number",
    value = st.session_state["t_pannello_pilota"],
    title = {'text': "Temperatura pannello pilota"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': st.session_state["t_pannello_pilota_old"]},
    gauge = {'axis': {'range': [None, 50]},
             'steps' : [
                 {'range': [0, 30], 'color': "lightgray"},
                 {'range': [30, 50], 'color': "gray"}],
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 45}})

fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{"type": "indicator"}, {"type": "indicator"}]],
    # subplot_titles=[f"Temperatura {n}" for n in range(11)]
    vertical_spacing=0.2,
    # row_heights=[0.9, 0.9, 0.9]
    horizontal_spacing=0.1

    )

fig.append_trace(fig_t_amb,row=1,col=1)
fig.append_trace(fig_t_pannello_pilota,row=1,col=2)

st.plotly_chart(fig,use_container_width=True)
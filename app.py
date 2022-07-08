from multiprocessing.connection import Client
import streamlit as st
from typing import List
import plotly.express as px
from CaprotoReaders.caproto_live_reader import CALiveReader
import time
from streamlit.scriptrunner.script_run_context import add_script_run_ctx
import pandas as pd

# import CA.Client.Exception

def get_pvs_from_txt(filename: str) -> List[str]:
    with open(filename) as file:
        lines = file.readlines()
    
    return lines

def main(title):
    # Set up page
    st.set_page_config(page_title=f"{title}", page_icon="✅", layout="wide")
    st.title(f"{title}")

    pv_col, data_points_col = st.columns([5, 5])
    with pv_col:
        selected_pvs = st.multiselect("Choose the IOC PVs you want to display:", get_pvs_from_txt("IOC_PVs.txt"))
    with data_points_col:
        num_data_points = st.slider("Select the number of data points to plot: ", min_value=50, max_value=10000)
    
    # Set up data reader
    reader = CALiveReader(selected_pvs, 50)

    reader.update()
    df = reader.df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.set_index('timestamp')
    chart = st.line_chart(df)

    while True:
        reader.update()
        df = reader.df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.set_index('timestamp')
        chart.add_rows(df.iloc[[-1]])
        time.sleep(.2)


if __name__ == "__main__":
    main("IOC display dashboard")

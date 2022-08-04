from mimetypes import init
import streamlit as st
import pandas as pd
import numpy as np
import time
import dummy_data_thread
import threading
from CaprotoReaders.caproto_live_reader import CALiveReader
from typing import List


def get_pvs_from_txt(filename: str) -> List[str]:
    with open(filename) as file:
        lines = file.readlines()

    return lines


TEST_DATA = "dummy"
if TEST_DATA == "dummy":
    AVAILABLE_PVS = [i for i in range(3)]
else:
    AVAILABLE_PVS = get_pvs_from_txt("IOC_PVs.txt")


@st.experimental_singleton
def initialize():
    if TEST_DATA == "dummy":
        data_gen = dummy_data_thread.DataGenerator(50)
    else:
        data_gen = CALiveReader(1, ["kern:mass", "kern:stability"], 10)
    data_gen.start()
    return data_gen


data_gen = initialize()
charts = []
selected_pvs = []
num_data_points = []

num_plots = st.slider("Number of plots", min_value=1, max_value=3)

for i in range(num_plots):
    with st.container():
        pv_col, data_points_col = st.columns([1, 1])

        with pv_col:
            selected_pvs.append(st.multiselect("Select param", AVAILABLE_PVS, key=i))
        with data_points_col:
            num_data_points.append(
                st.slider("Number of data points", min_value=100, max_value=1000, key=i)
            )

        charts.append(st.line_chart(data_gen.df.iloc[:, selected_pvs[i]]))

for i in range(1000000):
    for idx, chart in enumerate(charts):
        chart.line_chart(data_gen.df.iloc[:, selected_pvs[idx]])

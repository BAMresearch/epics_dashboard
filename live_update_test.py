from dataclasses import dataclass
import streamlit as st
import dummy_data_thread
from CaprotoReaders.caproto_live_reader import CALiveReader
from typing import List
import time


def get_pvs_from_txt(filename: str) -> List[str]:
    with open(filename) as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    return lines

def make_df_ready_to_plot(df, selected_pvs: List[str], num_data_points: int):
    df = df[["timestamp"] + selected_pvs]
    df = df.iloc[-num_data_points:]
    return df.set_index("timestamp")

TEST_DATA = "dummys"
if TEST_DATA == "dummy":
    AVAILABLE_PVS = [i for i in range(3)]
else:
    AVAILABLE_PVS = get_pvs_from_txt("IOC_PVs.txt")

@st.experimental_singleton
def initialize():
    if TEST_DATA == "dummy":
        data_gen = dummy_data_thread.DataGenerator(50)
    else:
        data_gen = CALiveReader(0.1, AVAILABLE_PVS, 1000)
    data_gen.start()
    return data_gen

@dataclass
class Selections:
    selected_pvs: List[List[str]]
    num_data_points: List[int]


title = "EPICS IOC display dashboard"
st.set_page_config(page_title=f"{title}", page_icon="✅", layout="wide")
st.title(f"{title}")

data_gen = initialize()
selections = Selections([], [])
charts = []

num_plots = st.slider("Select the number of plots you want: ", min_value=1, max_value=10)

for i in range(num_plots):
    with st.container():
        pv_col, data_points_col = st.columns([1, 1])

        with pv_col:
            selections.selected_pvs.append(st.multiselect("Choose the IOC PVs you want to display:", AVAILABLE_PVS, key=i))
        with data_points_col:
            selections.num_data_points.append(
                st.slider("Select the number of data points to plot: ", min_value=10, max_value=data_gen.max_num_values, key=i)
            )

        if TEST_DATA == "dummy":
            charts.append(st.line_chart(data_gen.df.iloc[:, selections.selected_pvs[i]]))
        else:
            data = make_df_ready_to_plot(data_gen.df, selections.selected_pvs[i], selections.num_data_points[i])
            charts.append(st.line_chart(data))

while True:
    for idx, chart in enumerate(charts):

        if TEST_DATA == "dummy":
            chart.line_chart(data_gen.df.iloc[:, selections.selected_pvs[idx]])
        else:
            data = make_df_ready_to_plot(data_gen.df, selections.selected_pvs[idx], selections.num_data_points[idx])

            try:
                chart.line_chart(data)
            except RuntimeError as e:
                # I can't figure out at the moment why this error comes up from time to time but for now we just pass it
                # and try again in the next while loop iteration.
                if not str(e) == "dictionary changed size during iteration":
                    raise
    
    time.sleep(0.1)
    
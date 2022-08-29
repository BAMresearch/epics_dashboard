from dataclasses import dataclass
import streamlit as st
from CaprotoReaders.caproto_live_reader import CALiveReader
from typing import List
import time
import plotly.express as px


def get_pvs_from_txt(filename: str) -> List[str]:
    with open(filename) as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if not line.startswith("#")]
    return lines


def make_df_ready_to_plot(
    df, selected_pvs: List[str], num_data_points: int, num_data_points_past: int
):
    df = df[["timestamp"] + selected_pvs]
    if num_data_points_past == 0:
        df = df.iloc[-num_data_points:]
    else:
        df = df.iloc[-(num_data_points + num_data_points_past) : -num_data_points_past]
    return df.set_index("timestamp")


AVAILABLE_PVS = get_pvs_from_txt("IOC_PVs.txt")


@st.experimental_singleton
def initialize():
    data_gen = CALiveReader(0.1, AVAILABLE_PVS, 10000)
    data_gen.start()
    return data_gen


@dataclass
class Selections:
    selected_pvs: List[List[str]]
    num_data_points: List[int]
    num_data_points_past: List[int]


title = "EPICS IOC display dashboard"
st.set_page_config(page_title=f"{title}", page_icon="✅", layout="wide")
st.title(f"{title}")

data_gen = initialize()
selections = Selections([], [], [])
charts = []

num_plots = st.slider(
    "Select the number of plots you want: ", min_value=1, max_value=10
)

update_frequency = st.text_input(
    "Choose the desired update frequency [Hz] for the dashboard data:", 10
)

try:
    data_gen.update_frequency = update_frequency
except ValueError as e:
    st.write(e)


for i in range(num_plots):
    with st.container():
        pv_col, data_points_col = st.columns([1, 1])

        with pv_col:
            selections.selected_pvs.append(
                st.multiselect(
                    "Choose the IOC PVs you want to display:", AVAILABLE_PVS, key=i
                )
            )
        with data_points_col:
            selections.num_data_points.append(
                st.slider(
                    "Select the number of data points to plot: ",
                    min_value=10,
                    max_value=data_gen.max_num_values,
                    key=2 * i,
                )
            )
            selections.num_data_points_past.append(
                st.slider(
                    "Select the number of data points you want to move the plot into the past: ",
                    min_value=0,
                    max_value=data_gen.max_num_values - 10,
                    key=2 * i + 1,
                )
            )

        data = make_df_ready_to_plot(
            data_gen.df,
            selections.selected_pvs[i],
            selections.num_data_points[i],
            selections.num_data_points_past[i],
        )
        fig = px.line(data, title="PV values over time")
        charts.append(st.plotly_chart(fig, use_container_width=True))

while True:
    for idx, chart in enumerate(charts):
        data = make_df_ready_to_plot(
            data_gen.df,
            selections.selected_pvs[idx],
            selections.num_data_points[idx],
            selections.num_data_points_past[idx],
        )

        try:
            fig = px.line(data, title="PV values over time")
            chart.plotly_chart(fig, use_container_width=True)
        except RuntimeError as e:
            # I can't figure out at the moment why this error comes up from time to time but for now we just pass it
            # and try again in the next while loop iteration.
            if not str(e) == "dictionary changed size during iteration":
                raise

    time.sleep(0.1)

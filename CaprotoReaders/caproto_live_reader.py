from datetime import datetime
from epics import caget
from nbformat import read
import pandas as pd
from typing import List
import time
import threading
import datetime
import epics


def get_time_different_formats():
    current_time = time.time()
    current_date_time = datetime.datetime.fromtimestamp(current_time)
    current_time_human_readable = current_date_time.strftime("%d-%m-%Y %H:%M:%S")
    return current_time, current_time_human_readable


class CALiveReader(threading.Thread):
    def __init__(self, update_time: float, pvs: List[str], max_num_values: int = 1000):
        """
        Retrieves and stores Caproto PVs live.

        Params:
            update_rate: Time in seconds in between updating the data. Absolute minimum 0.01. Minimum reliable approximately 0.1
            pvs: List of PVs to sample.
            max_num_values: Maximum number of values to be stored for each PV.
        """
        threading.Thread.__init__(self, daemon=True)
        self._update_time = update_time
        self._pvs = pvs
        self._max_num_values = max_num_values

        # Initialize dataframe
        self.df = pd.DataFrame(columns=self._pvs).astype(float)
        self.df["timestamp"] = ""

    # def add_pvs(self, pvs: List[str]):
    #     self._pvs.extend(pvs)

    # def remove_pvs(self, pvs: List[str]):
    #     for pv in pvs:
    #         try:
    #             self._pvs.remove(pv)
    #         except ValueError:
    #             raise ValueError(
    #                 f"{pv} could not be removed as it is currently not one of the tracked PVs."
    #             )

    def run(self):
        current_time, current_time_human_readable = get_time_different_formats()
        while True:
            try:
                # Retrieve values
                values = []
                for pv in self._pvs:
                    values.append(caget(pv, timeout=1.0))

                values.append(current_time_human_readable)

                # Add values to dataframe
                assert (
                    len(values) == len(self._pvs) + 1
                ), "Number of retrieved values does not equal the number of PVs to check."
                self.df.loc[len(self.df)] = values

                # Ensure that the maximum number of values to be stored in the dataframe is not exceeded
                num_values_to_remove = self.df.shape[0] - self._max_num_values
                if num_values_to_remove > 0:
                    self.df = (
                        self.df.iloc[num_values_to_remove:]
                        .reset_index()
                        .drop(columns=["index"])
                    )

            except epics.ca.ChannelAccessGetFailure:
                # Thiss exception has only been raised once so far. Won't investigate for now but rather ignore it
                print(
                    "WARNING: Exception 'epics.ca.ChannelAccessGetFailure' has been raised but is ignored for now."
                )

            while time.time() <= current_time + self._update_time:
                time.sleep(0.01)

            current_time, current_time_human_readable = get_time_different_formats()

    @property
    def max_num_values(self):
        return self._max_num_values


if __name__ == "__main__":
    reader = CALiveReader(1, ["kern:mass", "kern:stability"], 10)
    reader.start()
    while True:
        print(reader.df)

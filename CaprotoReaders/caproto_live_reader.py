from datetime import datetime
from epics import caget
from nbformat import read
import pandas as pd
from typing import List
import time
import threading


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
        current_time = time.time()
        while True:
            # Retrieve values
            values = []
            for pv in self._pvs:
                values.append(caget(pv))

            values.append(current_time)

            # Add values to dataframe
            assert (
                len(values) == len(self._pvs) + 1
            ), "Number of retrieved values does not equal the number of PVs to check."
            self.df.loc[len(self.df)] = values
            # new_row = {}
            # for pv in self._pvs:
            #     new_row[pv] = values.pop(0)
            # new_row["timestamp"] = values.pop()
            # assert len(values) == 0
            # self.df = self.df.append(new_row, ignore_index=True)

            # Ensure that the maximum number of values to be stored in the dataframe is not exceeded
            num_values_to_remove = self.df.shape[0] - self._max_num_values
            if num_values_to_remove > 0:
                self.df = self.df.iloc[num_values_to_remove:]

            while time.time() <= current_time + self._update_time:
                time.sleep(0.01)

            current_time = time.time()


if __name__ == "__main__":
    reader = CALiveReader(0.01, ["kern:mass", "kern:stability"], 10)
    reader.start()
    print(reader.df)

from datetime import datetime
from epics import caget
from nbformat import read
import pandas as pd
from typing import List
import time
import threading


class CALiveReader:
    def __init__(self, pvs: List[str], max_num_values: int = 50):
        """
        Retrieves and stores Caproto PVs live.

        Params:
            pvs: List of PVs to sample.
            max_num_values: Maximum number of values to be stored for each PV.
        """
        self._pvs = pvs
        self._max_num_values = max_num_values

        # Initialize dataframe
        self.df = pd.DataFrame(columns=self._pvs).astype(float)
        self.df["timestamp"] = ""

    def add_pvs(self, pvs: List[str]):
        self._pvs.extend(pvs)

    def remove_pvs(self, pvs: List[str]):
        for pv in pvs:
            try:
                self._pvs.remove(pv)
            except ValueError:
                raise ValueError(f"{pv} could not be removed as it is currently not one of the tracked PVs.")

    def update(self):
        current_time = time.time()

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


if __name__ == "__main__":
    reader = CALiveReader(.01, ["kern:mass", "kern:stability"], 10)

    while True:
        time.sleep(2)
        reader.update()
        print(reader.df)

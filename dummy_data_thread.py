import threading
import pandas as pd
import numpy as np
import time


class DataGenerator(threading.Thread):
    def __init__(self, n):
        threading.Thread.__init__(self, daemon=True)
        self.df = pd.DataFrame(
            np.random.randn(n, 3), columns=("col %d" % i for i in range(3))
        )
        self.df["index"] = np.arange(n)
        self.df.set_index("index", inplace=True)

    def run(self):
        while True:
            self.df = self.df.iloc[1:]
            df2 = pd.DataFrame(
                np.random.randn(1, 3), columns=("col %d" % e for e in range(3))
            )
            new_index = self.df.iloc[-1].name + 1
            df2["index"] = new_index
            df2.set_index("index", inplace=True)
            self.df = pd.concat(
                [self.df, df2],
            )


if __name__ == "__main__":
    thread = DataGenerator(10)
    # thread.start()
    print(thread.df.iloc[:, 0])

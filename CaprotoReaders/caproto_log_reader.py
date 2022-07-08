import pandas as pd


class CALogReader:
    def __init__(self, log_path: str):
        # read the log file, put in columns. Unfortunately, due to the space, the datetime stamp is being put in two separate columns, but we'll fix that next.
        self.raw_time_series = pd.read_csv(
            log_path,
            sep="\s+",
            skipinitialspace=True,
            names=["source", "date", "time", "val"],
        )
        # remove square brackets from values, these came from the monitor process, but we're not receiving lists or anything:
        self.raw_time_series["val"] = (
            self.raw_time_series["val"]
            .str.replace("[\[\]]", "", regex=True)
            .astype(float)
        )
        # convert date and time columns into a datetime column
        self.raw_time_series["datetime"] = pd.to_datetime(
            self.raw_time_series["date"] + " " + self.raw_time_series["time"]
        )

        # Remove duplicates
        self.raw_time_series.drop_duplicates(inplace=True)

        # Add timedelta column
        self.raw_time_series["timedelta"] = (
            self.raw_time_series["datetime"] - self.raw_time_series["datetime"].min()
        )

    def get_unique_keys(self):
        return self.raw_time_series.source.unique()

    def get_df_with_datetime_idx(self):
        return self.raw_time_series.pivot(
            index="datetime", columns="source", values="val"
        )

    @property
    def time_max(self):
        return self.raw_time_series["datetime"].max()

    @property
    def time_min(self):
        return self.raw_time_series["datetime"].min()

    @property
    def time_span(self):
        return self.time_max - self.time_min

    @property
    def mean_values_per_hour(self):
        """group by source, show mean values per hour"""
        return self.raw_time_series.groupby(
            [self.raw_time_series["datetime"].dt.hour, "source"]
        )["val"].mean()

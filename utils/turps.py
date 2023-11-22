#!/usr/bin/env python3
"""Loads a DAS excel spreadsheet and linearly interpolates between each point to make a single table."""
import argparse
import pandas as pd
from typing import List, Tuple, TypeVar, Callable
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime

T = TypeVar("T")


class ColumnModifier(ABC):
    """Base class for a modifier that can modify or process individual columns in individual sheets."""

    @abstractmethod
    def __init__(self, column_name: str, sheet_name: str = None):
        """Initialises the modifier with the column name and sheet(s) to look for.

        Args:
            column_name (str): the column name to be applied to.
            sheet_name (str, optional): A specific shee to apply to only. Defaults to None.
        """
        self.sheet_name = sheet_name
        self.column_name = column_name

    def apply(self, sheet_name: str, sheet: pd.DataFrame):
        """Applies this modifier to a sheet if required.

        Args:
            sheet_name (str): The name of the current sheet.
            sheet (pd.DataFrame): The dataframe object containing the sheet. This is updated on return.
        """
        if (self.sheet_name is None or sheet_name == self.sheet_name) and (
            self.column_name in sheet
        ):
            # We should take notice of this sheet and the column is present.
            sheet[self.column_name] = self.modify(sheet[self.column_name])

    @abstractmethod
    def modify(self, column: pd.Series) -> pd.Series:
        """Applies the modifier to the column.

        Args:
            column (pd.Series): The input data.

        Returns:
            pd.Series: The modified data.
        """
        pass


class GPSTimestampModifier(ColumnModifier):
    """Class for converting the GPS timestamps to unix timestamps."""

    def __init__(self):
        """Initialises the modifier."""
        super().__init__("3_gps_datetime", "module_3_data")

    def modify(self, column: pd.Series) -> pd.Series:
        """Applies the modifier to the column.

        Args:
            column (pd.Series): The input data.

        Returns:
            pd.Series: The modified data.
        """

        def convert_gps(time_str: str) -> float:
            """Converts a timestamp to a floating point unix time."""
            try:
                time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                return time_obj.timestamp()
            except ValueError:
                # If the GPS doesn't have lock, sometimes it gives a date with day 0.
                return 0

        return column.apply(convert_gps)


def load(
    excel: pd.ExcelFile,
    excluded_sheets: List[str] = [],
    modifiers: List[ColumnModifier] = [],
) -> List[pd.DataFrame]:
    """Returns a list of sheets to merge.

    Args:
        excel (pd.ExcelFile): The spreadsheet to load.
        excluded_sheets (List[str], optional): Sheet names to exclude. Defaults to [].
        modifiers (List[ColumnModifier, optional]): Modifies the values in particular columns for easier processing. Defaults to [].

    Returns:
        List[pd.DataFrame]: A list of all sheets.
    """
    sheets = []
    for i in excel.sheet_names:
        if i not in excluded_sheets:
            # Add an interpolator for this sheet.
            sheets.append(excel.parse(i))

            # Apply the modifiers if needed
            for m in modifiers:
                m.apply(i, sheets[-1])

    return sheets


def time_getter(aggregator: Callable[[float], T]) -> Callable[[pd.DataFrame], T]:
    """Returns a function that can aggregate the time field in a specific way."""
    return lambda frame: aggregator(frame["unix_time"])


max_time = time_getter(max)
min_time = time_getter(min)


def get_after(frame: pd.DataFrame, time: float) -> pd.Series:
    """Gets the first row on or after a specific time.

    Args:
        frame (pd.DataFrame): The dataframe to search in.
        time (float): The time to search for.

    Returns:
        pd.Series: The first row on or after the time.
    """
    time_comparisons = frame["unix_time"] >= time
    after = frame[time_comparisons]
    if len(after):
        return after.iloc[0]
    else:
        return None


def get_before(frame: pd.DataFrame, time: float) -> pd.Series:
    """Gets the first row on or before a specific time.

    Args:
        frame (pd.DataFrame): The dataframe to search in.
        time (float): The time to search for.

    Returns:
        pd.Series: The first row on or before the time.
    """
    time_comparisons = frame["unix_time"] <= time
    before = frame[time_comparisons]
    if len(before):
        return before.iloc[-1]
    else:
        return None


def interpolate(
    t1: float, t2: float, n1: float, n2: float, time_target: float
) -> float:
    """Linearly interpolates between two points.

    Args:
        t1 (float): The time of the first point.
        t2 (float): The time of the second point.
        n1 (float): The value of the first point.
        n2 (float): The value of the second point.
        time_target (float): The time to estimate the value of.

    Returns:
        float: The linearly interpolated value at time_target.
    """
    if t1 == t2:
        # Rows have the same time. Averate the values as gradient is undefined.
        return (n1 + n2) / 2
    else:
        # y - y1 = m(x - x1)
        # m = (y2 - y1) / (x2 - x1)
        m = (n1 - n2) / (t1 - t2)
        return m * (time_target - t1) + n1


def interpolate_rows(row1: pd.Series, row2: pd.Series, time: float) -> pd.Series:
    """Interpolates between two rows with the same columns.

    Args:
        row1 (pd.Series): The first row.
        row2 (pd.Series): The second row.
        time (float): The time to interpolate at.

    Returns:
        pd.Series: The merged row.
    """

    time_column = "unix_time"
    t1 = row1[time_column]
    t2 = row2[time_column]

    # Row to put stuff in.
    new_row = row1.copy()
    new_row[time_column] = time

    # TODO: Cope with strings and GPS timestamps

    # Iterate over all non-time columns.
    for column in row1.keys():
        if column != time_column:
            # A row that isn't the time. Interpolate between.
            new_row[column] = interpolate(t1, t2, row1[column], row2[column], time)

    return new_row


def merge(sheets: List[pd.DataFrame], t_step=1) -> pd.DataFrame:
    """Merges all sheets into one by interpolating between them and resampling.

    Args:
        sheets (List[pd.DataFrame]): The sheets to merge.

    Returns:
        pd.DataFrame: The merged and interpolated data frame.
    """
    times, data = resample_sheets(sheets, t_step)
    # print(repr(data[0]))
    for i, time in enumerate([times[10]]):
        print(repr(pd.concat(data[i], axis=1)))   


def resample_sheets(
    sheets: List[pd.DataFrame], t_step: float = 1
) -> Tuple[List[float], List[List[pd.DataFrame]]]:
    """Resamples all sheets to have the same times.

    Args:
        sheets (List[pd.DataFrame]): The sheets to merge.
        t_step (float): The time step.

    Returns:
        Tuple[List[float], List[List[pd.DataFrame]]]: The times and for each time, a list of Series for each sheet.
    """
    # Maximum and minimum times to interpolate between
    min_t = min([min_time(i) for i in sheets])
    max_t = max([max_time(i) for i in sheets])

    rows = []
    times = np.arange(min_t, max_t, t_step)
    for time in times:
        time_rows = []
        for sheet in sheets:
            # Get the row before the current time and after for the current sheet.
            before = get_before(sheet, time)
            after = get_after(sheet, time)

            if after is not None and before is None:
                # At the very beginning of this sheet.
                time_rows.append(after)
            elif before is not None and after is None:
                # At the very end of this sheet.
                time_rows.append(before)
            else:
                # There are two rows. Linearly interpolate.
                # time_rows.app
                time_rows.append(interpolate_rows(before, after, time))

        rows.append(time_rows)
    
    return times, rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "turps", "linearly interpolates between DAS log files and merges all tabes"
    )
    parser.add_argument("-i", "--input", help="The input file", type=str, required=True)
    args = parser.parse_args()
    sheets = load(pd.ExcelFile(args.input), ["raw_data"], [GPSTimestampModifier()])
    merge(sheets)

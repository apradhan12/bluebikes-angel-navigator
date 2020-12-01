#!/usr/bin/env python3

import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy as np
import sys

station_id = None
OVERLAY_SINGLE_DAY = True
INCLUDE_LEGEND = False

SHADED_REGION_COLOR = (0, 1, 1)
SHADED_REGION_ALPHA = 0.5
WEEK_START_LINE_COLOR = (0.2, 0.2, 0.2)
NORMAL_DAY_LINE_COLOR = (0.5, 0.5, 0.5)


def process_file_contents(timestamp, contents):
    if station_id in contents:
        return contents[station_id]
    else:
        raise Exception(f"{station_id} is not present at timestamp {timestamp}")


def initialize_current_date_data(arrays):
    # initialize current_date_data to the same number of empty arrays as there are variables
    current_date_data = []
    for _ in range(len(arrays) + 1):  # add one extra empty array for timestamps
        current_date_data.append([])
    return current_date_data


def split_dates_and_modulo_time(timestamps, arrays,
                                date_lambda=lambda dt: dt.date(),
                                time_lambda=lambda dt: dt.time().hour + dt.time().minute / 60):
    """
    :param time_lambda: lambda to get time of day from datetime object
                        (result needs to eventually be parsed to float for matplotlib, if not float already)
    :param date_lambda: lambda to convert datetime object to date
    :param timestamps: an array of the timestamps for all the data points (sorted ascending)
    :param arrays: an array of arrays of values for each of the other variables
    :return: an array where each element represents a date, in which each array contains arrays
             for all the variables (where time of day is inserted as the first array in each array of arrays)
    """
    dates_data = []
    current_date_data = []
    previous_date = None
    for i, timestamp in enumerate(timestamps):
        # print(timestamp)
        if previous_date is None:
            previous_date = date_lambda(timestamp)
            current_date_data = initialize_current_date_data(arrays)
        elif date_lambda(timestamp) != previous_date:
            # print(f"{date_lambda(timestamp)} != {previous_date}")
            dates_data.append(current_date_data)
            previous_date = date_lambda(timestamp)
            current_date_data = initialize_current_date_data(arrays)
        # print(current_date_data)

        # add the data from the current timestamp
        current_date_data[0].append(time_lambda(timestamp))
        for j, array in enumerate(arrays):
            current_date_data[j + 1].append(array[i])
    dates_data.append(current_date_data)

    return dates_data


def add_weekday_lines(start_date, end_date):
    """
    Add lines to the plot to distinguish different days of the week.
    """
    while start_date <= end_date:
        if start_date.weekday() == 0:  # draw a darker line at the start of the week
            plt.axvline(x=start_date, c=WEEK_START_LINE_COLOR)
        elif start_date.weekday() == 5:  # shade the weekend days to distinguish them
            plt.axvline(x=start_date, c=NORMAL_DAY_LINE_COLOR)
            plt.axvspan(start_date, start_date + timedelta(days=2),
                        alpha=SHADED_REGION_ALPHA, color=SHADED_REGION_COLOR)
        else:
            plt.axvline(x=start_date, c=NORMAL_DAY_LINE_COLOR)
        start_date += timedelta(days=1)


def main():
    global station_id
    station_id = sys.argv[1]

    timestamps = []
    active = []
    bikes = []
    bikes_and_docks = []
    capacities = []
    points = []

    start_date = None
    end_time = None

    # read all the files in the processed_output directory to obtain timeseries data
    filenames = os.listdir("processed_output/")
    if not filenames:
        raise Exception("no files found in processed_output/")

    for filename in filenames:
        with open(f"processed_output/{filename}") as file_stream:
            contents = json.load(file_stream)
            timestamp = datetime.fromtimestamp(int(filename.split(".")[0]))
        if start_date is None:
            # gets the start date as a date object (with 00:00 as the time of day)
            start_date = datetime.combine(timestamp.date(), datetime.min.time())
        end_time = timestamp  # todo: Is there a more efficient way to do this than reassigning this each loop?
        id_contents = process_file_contents(timestamp, contents)
        timestamps.append(timestamp)

        # The following lines depend on the serialization format from
        # process_data.py - should this be standardized/documented?
        active.append(id_contents[0])  # TODO: incorporate this into the plot?
        bikes.append(id_contents[1])
        bikes_and_docks.append(id_contents[1] + id_contents[2])
        capacities.append(id_contents[3])
        if len(id_contents) == 5:
            points.append(id_contents[4])
        else:
            points.append(None)
    end_date = datetime.combine(end_time.date(), datetime.min.time())

    # read the name of the station whose ID was specified as a command-line argument
    with open("overall_stations.txt") as file_stream:
        contents = json.load(file_stream)
    name = contents[station_id]["name"][-1][1]

    # TODO: deal with inactive stations

    # create the plot
    if OVERLAY_SINGLE_DAY:
        for i, date_array in enumerate(split_dates_and_modulo_time(timestamps, [points])):
            if i % 7 in [0, 1, 2, 3, 6]:
                for variable_array in date_array[1:]:
                    # [x % 2 if x is not None else None for x in variable_array]
                    plt.plot(date_array[0], [x % 2 if x is not None else None for x in variable_array], label=i)
        plt.axis(ymin=-3, ymax=3)
        # replace "on weekdays" appropriately
        plt.title(f"Angel point values on weekdays at {name} (station ID {station_id})")
    else:
        plt.axis(ymin=-3)
        plt.title(f"Bike capacity at {name} (station ID {station_id})")
        plt.plot(timestamps, bikes, label="# Bikes")
        plt.plot(timestamps, bikes_and_docks, label="# Bikes + Docks")
        plt.plot(timestamps, capacities, label="Capacity")
        plt.plot(timestamps, points, label="Angel Points")
        add_weekday_lines(start_date, end_date)

    if INCLUDE_LEGEND:
        plt.legend()

    # add labels/ticks to the plot, and then show it
    plt.xlabel("Date/Time")
    xmin, xmax, ymin, ymax = plt.axis()
    plt.yticks(np.arange(ymin, ymax + 1, step=1))

    plt.show()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy as np
import sys

station_id = None
OVERLAY_SINGLE_DAY = False


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
                                time_lambda=lambda dt: dt.time()):
    """
    :param time_lambda: lambda to get time of day from datetime object
    :param date_lambda: lambda to convert datetime object to date
    :param timestamps: an array of the timestamps for all the data points (sorted ascending)
    :param arrays: an array of arrays of values for each of the other variables
    :return: an array where each element represents a date, in which each array contains arrays
             for all the variables (including timestamp)
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
    while start_date <= end_date:
        if start_date.weekday() == 0:
            plt.axvline(x=start_date, c=(0.2, 0.2, 0.2))
        elif start_date.weekday() == 5:
            plt.axvline(x=start_date, c=(0.5, 0.5, 0.5))
            plt.axvspan(start_date, start_date + timedelta(days=2), alpha=0.5, color=(0, 1, 1))
        else:
            plt.axvline(x=start_date, c=(0.5, 0.5, 0.5))
        start_date += timedelta(days=1)


def main():
    assert split_dates_and_modulo_time([0, 1, 2, 3], [[1, 1, 2, 2], [3, 3, 4, 4]],
                                       date_lambda=lambda x: x // 2, time_lambda=lambda x: x % 2) == \
           [[[0, 1], [1, 1], [3, 3]], [[0, 1], [2, 2], [4, 4]]]

    global station_id

    timestamps = []
    valid = []
    bikes = []
    bikes_and_docks = []
    capacities = []
    points = []

    station_id = sys.argv[1]

    start_date = None
    end_time = None

    filenames = os.listdir("processed_output/")
    if not filenames:
        raise Exception("no files found in processed_output/")

    for filename in filenames:
        with open(f"processed_output/{filename}") as file_stream:
            contents = json.load(file_stream)
            timestamp = datetime.fromtimestamp(int(filename.split(".")[0]))
        if start_date is None:
            start_date = datetime.combine(timestamp.date(), datetime.min.time())
        end_time = timestamp  # todo: make this better
        id_contents = process_file_contents(timestamp, contents)
        timestamps.append(timestamp)
        valid.append((0, 1, 0) if id_contents[0] else (0, 0.5, 0))
        bikes.append(id_contents[1])
        bikes_and_docks.append(id_contents[1] + id_contents[2])
        capacities.append(id_contents[3])
        if len(id_contents) == 5:
            points.append(id_contents[4])
        else:
            points.append(None)

    with open("overall_stations.txt") as file_stream:
        contents = json.load(file_stream)
    name = contents[station_id]["name"][-1][1]

    end_date = datetime.combine(end_time.date(), datetime.min.time())

    # TODO: deal with inactive stations
    if OVERLAY_SINGLE_DAY:
        for i, date_array in enumerate(split_dates_and_modulo_time(timestamps, [bikes])):
            if i % 7 == 2:
                for variable_array in date_array[1:]:
                    # the date you put in here doesn't matter - just a filler
                    # TODO: graph by hour of day instead??? or maybe just change x-axis labels
                    plt.plot([datetime.combine(start_date, t) for t in date_array[0]], variable_array, label=i)
    else:
        plt.plot(timestamps, bikes, label="# Bikes")
        plt.plot(timestamps, bikes_and_docks, label="# Bikes + Docks")
        plt.plot(timestamps, capacities, label="Capacity")
        plt.plot(timestamps, points, label="Angel Points")
        add_weekday_lines(start_date, end_date)

    plt.legend()
    plt.title(f"Bike capacity at {name} (station ID {station_id})")

    plt.xlabel("Date/Time")
    xmin, xmax, ymin, ymax = plt.axis(ymin=-3)
    plt.yticks(np.arange(ymin, ymax + 1, step=1))

    plt.show()


if __name__ == "__main__":
    main()

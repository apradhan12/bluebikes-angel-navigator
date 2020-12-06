#!/usr/bin/env python3
import math
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy as np
import statistics
import sys

OVERLAY_SINGLE_DAY = True
INCLUDE_LEGEND = False

SHADED_REGION_COLOR = (0, 1, 1)
SHADED_REGION_ALPHA = 0.5
WEEK_START_LINE_COLOR = (0.2, 0.2, 0.2)
NORMAL_DAY_LINE_COLOR = (0.5, 0.5, 0.5)


# def process_file_contents(timestamp, contents, all_timestamps):
#     """Processes the file contents and adds the relevant data to all_timestamps"""
#     # all_timestamps = {
#     #     "10": {
#     #         "3": 30,
#     #         "4": 15
#     #     },
#     #     "11": {
#     #         "3": 32,
#     #         "4": 12
#     #     }
#     # }
#     relevant_contents = {}
#     for station_id, data in contents.items():
#         relevant_contents[station_id] = data[]



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


def datetime_to_date(dt):
    """
    Gets a date from a datetime, i.e. the corresponding datetime object with the time of day set to midnight.
    """
    return datetime.combine(dt.date(), datetime.min.time())


def is_one_hour_after(dt2, dt1):
    """Is floor(dt2) exactly 1 hour after floor(dt1)?"""
    if dt1.date() == dt2.date():
        return dt2.hour - dt1.hour == 1
    if dt2.date() - dt1.date() == timedelta(days=1):
        return dt2.hour == 0 and dt1.hour == 23
    return False


def in_time_interval(dt):
    weekdays = [0, 1, 2, 3, 4]
    hour = 17
    return dt.weekday() in weekdays and dt.hour == hour


def average_to_color(avg):
    green = 1 / (1 + math.e ** -avg)
    red = 1 - (1 / (1 + math.e ** -avg))
    return red, green, 0


def stdev_to_size(stdev):
    return 20 * (1.3 ** -stdev)


def main():
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

    previous_date = None
    previous_hour = None

    # all_timestamps = {
    #     "10": { station id
    #         "3": [30, 15], timestamp: [values]
    #         "4": [15, 3]
    #     },
    #     "11": {
    #         "3": [32, 13],
    #         "4": [12, 6]
    #     }
    # }
    all_stations = {}

    for filename in filenames:
        timestamp = int(filename.split(".")[0])
        dt = datetime.fromtimestamp(timestamp)
        if previous_hour is None or previous_date != dt.date() or previous_hour != dt.hour:
            with open(f"processed_output/{filename}") as file_stream:
                contents = json.load(file_stream)
                for station, values in contents.items():
                    if station not in all_stations:
                        all_stations[station] = {}
                    all_stations[station][timestamp] = contents[station][1]  # only tracking number of bikes for now
            previous_date = dt.date()
            previous_hour = dt.hour

    all_station_statistics = {}
    for station in all_stations:
        timestamp_items = list(all_stations[station].items())
        deltas = []
        for i in range(len(timestamp_items) - 1):
            first = timestamp_items[i]  # e.g. (123456789, 12)
            second = timestamp_items[i + 1]
            first_dt = datetime.fromtimestamp(first[0])
            second_dt = datetime.fromtimestamp(second[0])
            if is_one_hour_after(second_dt, first_dt):
                if in_time_interval(first_dt):
                    deltas.append(second[1] - first[1])
                else:
                    pass
                    # print(f"Weekday is {first_dt.weekday()} and time is {first_dt.hour}, skipping")
            else:
                print(f"Timestamp delta is {second_dt - first_dt}, skipping")
        avg = sum(deltas) / len(deltas) if deltas else None
        stdev = statistics.stdev(deltas) if len(deltas) >= 2 else None
        all_station_statistics[station] = [avg, stdev]

    station_ids_list, station_statistics_list = zip(*all_station_statistics.items())
    averages_list, stdevs_list = zip(*station_statistics_list)
    colors_list = [average_to_color(avg) for avg in averages_list]
    sizes_list = [stdev_to_size(stdev) for stdev in stdevs_list]
    longitudes_list = []
    latitudes_list = []

    # get the station coords
    with open("overall_stations.txt") as file_stream:
        contents = json.load(file_stream)
    for station_id in station_ids_list:
        latitudes_list.append(contents[station_id]["coords"][-1][1][0])
        longitudes_list.append(contents[station_id]["coords"][-1][1][1])

    UPPER_LEFT_CORNER = (42.4379, -71.3538)
    LOWER_RIGHT_CORNER = (42.2059, -70.8148)

    BBox = (UPPER_LEFT_CORNER[1], LOWER_RIGHT_CORNER[1],
            LOWER_RIGHT_CORNER[0], UPPER_LEFT_CORNER[0])

    boston = plt.imread("map.png")

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(longitudes_list, latitudes_list, zorder=1, alpha=1.0, c=colors_list, s=sizes_list)
    ax.set_title('Bike Stations')
    ax.set_xlim(BBox[0], BBox[1])
    ax.set_ylim(BBox[2], BBox[3])
    ax.imshow(boston, zorder=0, extent=BBox, aspect="auto")
    plt.show()

    # # create the plot
    # if OVERLAY_SINGLE_DAY:
    #     variables_to_graph = [points]  # change this to add more variables to the plot (doesn't work well currently)
    #     for i, date_array in enumerate(split_dates_and_modulo_time(timestamps, variables_to_graph)):
    #         if i % 7 in [0, 1, 2, 3, 6]:
    #             for variable_array in date_array[1:]:
    #                 # [x % 2 if x is not None else None for x in variable_array]
    #                 plt.plot(date_array[0], variable_array, label=i)
    #     plt.axis(ymin=-3, ymax=3)
    #     # replace "on weekdays" appropriately
    #     plt.title(f"Angel point values on weekdays at {name} (station ID {station_id})")
    # else:
    #     plt.axis(ymin=-3)
    #     plt.title(f"Bike capacity at {name} (station ID {station_id})")
    #     plt.plot(timestamps, bikes, label="# Bikes")
    #     plt.plot(timestamps, bikes_and_docks, label="# Bikes + Docks")
    #     plt.plot(timestamps, capacities, label="Capacity")
    #     plt.plot(timestamps, points, label="Angel Points")
    #     add_weekday_lines(start_date, end_date)
    #
    # if INCLUDE_LEGEND:
    #     plt.legend()
    #
    # # add labels/ticks to the plot, and then show it
    # plt.xlabel("Date/Time")
    # xmin, xmax, ymin, ymax = plt.axis()
    # plt.yticks(np.arange(ymin, ymax + 1, step=1))
    #
    # plt.show()


if __name__ == "__main__":
    main()

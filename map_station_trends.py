#!/usr/bin/env python3

import math
import os
import json
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from datetime import datetime
from datetime import timedelta
from geopy.distance import distance
import statistics
import argparse

UPPER_LEFT_CORNER = (42.4379, -71.3538)
LOWER_RIGHT_CORNER = (42.2059, -70.8148)

RADIUS_MILES = 0.5
MIN_DIFF_HOUR_BIKES_DELTA = 2.5
MIN_DIFF_HOUR_POINTS = 1

# must be either True/False or False/True for now
USE_POINTS = True
SHOW_RATE_OF_CHANGE = False


def is_one_hour_after(dt2, dt1):
    """Is floor(dt2) exactly 1 hour after floor(dt1)?"""
    if dt1.date() == dt2.date():
        return dt2.hour - dt1.hour == 1
    if dt2.date() - dt1.date() == timedelta(days=1):
        return dt2.hour == 0 and dt1.hour == 23
    return False


def in_time_interval(dt, desired_hour, is_weekend):
    if is_weekend:
        desired_days = [5, 6]
    else:
        desired_days = [0, 1, 2, 3, 4]
    return dt.weekday() in desired_days and dt.hour == desired_hour


def average_to_color(avg):
    green = 1 / (1 + math.e ** -avg)
    red = 1 - (1 / (1 + math.e ** -avg))
    return red, green, 0


def stdev_to_size(avg, stdev):
    if abs(avg) > 1:
        return 200 * (2 ** (-1 * stdev))
    return 20


# def buildmebarchart(i=int):
#     plt.legend(df1.columns)
#     p = plt.plot(df1[:i].index, df1[:i].values)  # note it only returns the dataset, up to the point i
#     for i in range(0, 4):
#         p[i].set_color(color[i])  # set the colour of each curve


def draw(ax, desired_hour, is_weekend, longitudes_list, latitudes_list, colors_list, sizes_list, station_ids_list, lines, stdevs_list):
    # fig, ax = plt.subplots()
    ax.scatter(longitudes_list, latitudes_list, zorder=2, alpha=1.0, c=colors_list, s=sizes_list)
    for i, station_id in enumerate(station_ids_list):
        ax.annotate(station_id, (longitudes_list[i], latitudes_list[i]), fontsize="xx-small", zorder=3)
    for line in lines:
        plt.plot(line[0], line[1], c="b", zorder=1)
    if SHOW_RATE_OF_CHANGE:
        ax.set_title(
            f"Change in number of {'points' if USE_POINTS else 'bikes'} from {desired_hour}:00 to "
            f"{(desired_hour + 1) % 24}:00 on {'weekends' if is_weekend else 'weekdays'}")
    else:
        ax.set_title(
            f"Number of {'points' if USE_POINTS else 'bikes'} from {desired_hour}:00 to "
            f"{(desired_hour + 1) % 24}:00 on {'weekends' if is_weekend else 'weekdays'}")
    textstr = "\n".join((
        r"$\mu=%.3f$" % (sum(stdevs_list) / len(stdevs_list)),
        r"$\sigma=%.3f$" % statistics.stdev(stdevs_list)))
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hour")
    parser.add_argument("-w", "--weekend", help="show weekends", action="store_true")
    args = parser.parse_args()
    desired_hour = int(args.hour)
    is_weekend = args.weekend

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
                    if USE_POINTS:
                        all_stations[station][timestamp] = contents[station][4] if len(contents[station]) == 5 else 0
                    else:  # bikes
                        all_stations[station][timestamp] = contents[station][1]
            previous_date = dt.date()
            previous_hour = dt.hour

    all_station_statistics = {}
    for station in all_stations:
        timestamp_items = list(all_stations[station].items())
        if SHOW_RATE_OF_CHANGE:  # can show values themselves, or rate of change from value to value
            values = []
            for i in range(len(timestamp_items) - 1):
                first = timestamp_items[i]  # e.g. (123456789, 12)
                second = timestamp_items[i + 1]
                first_dt = datetime.fromtimestamp(first[0])
                second_dt = datetime.fromtimestamp(second[0])
                if is_one_hour_after(second_dt, first_dt):
                    if in_time_interval(first_dt, desired_hour, is_weekend):
                        values.append(second[1] - first[1])
                    else:
                        pass
                        # print(f"Weekday is {first_dt.weekday()} and time is {first_dt.hour}, skipping")
                else:
                    pass
                    # print(f"Timestamp delta is {second_dt - first_dt}, skipping")
        else:
            values = [ts_item[1] for ts_item in timestamp_items if
                      in_time_interval(datetime.fromtimestamp(ts_item[0]), desired_hour, is_weekend)]
        if len(values) < 2:
            raise ValueError(f"len(values) is < 2 for id {station}")

        avg = sum(values) / len(values) if values else None
        stdev = statistics.stdev(values) if len(values) >= 2 else None
        all_station_statistics[station] = [avg, stdev]

    station_ids_list, station_statistics_list = zip(*all_station_statistics.items())
    averages_list, stdevs_list = zip(*station_statistics_list)
    print(json.dumps(sorted(
        zip([round(avg, ndigits=2) for avg in averages_list], [round(stdev, ndigits=2) for stdev in stdevs_list],
            station_ids_list))))
    # print(sorted([round(avg, ndigits=2) for avg in averages_list]))
    # print(stdevs_list)
    print(sum(stdevs_list) / len(stdevs_list))
    print(statistics.stdev(stdevs_list))
    colors_list = [average_to_color(avg) for avg in averages_list]
    sizes_list = [stdev_to_size(avg, stdev) for avg, stdev in zip(averages_list, stdevs_list)]
    longitudes_list = []
    latitudes_list = []

    # get the station coords
    with open("overall_stations.txt") as file_stream:
        contents = json.load(file_stream)
    for station_id in station_ids_list:
        latitudes_list.append(contents[station_id]["coords"][-1][1][0])
        longitudes_list.append(contents[station_id]["coords"][-1][1][1])

    bbox = (UPPER_LEFT_CORNER[1], LOWER_RIGHT_CORNER[1],
            LOWER_RIGHT_CORNER[0], UPPER_LEFT_CORNER[0])

    boston = plt.imread("map.png")

    lines = []
    for i, sid1 in enumerate(station_ids_list):
        for j in range(i + 1, len(station_ids_list)):
            coords1 = (latitudes_list[i], longitudes_list[i])
            coords2 = (latitudes_list[j], longitudes_list[j])
            avg1 = averages_list[i]
            avg2 = averages_list[j]
            if USE_POINTS and not SHOW_RATE_OF_CHANGE:  # TODO: update this when we add more options
                surpasses_min_diff = abs(avg1 - avg2) > MIN_DIFF_HOUR_POINTS
            else:
                surpasses_min_diff = abs(avg1 - avg2) > MIN_DIFF_HOUR_BIKES_DELTA
            if distance(coords1, coords2).miles < RADIUS_MILES and surpasses_min_diff:
                lines.append(([coords1[1], coords2[1]], [coords1[0], coords2[0]]))
                # plt.plot([coords1[1], coords2[1]], [coords1[0], coords2[0]], c="b", zorder=1)
    fig, ax = plt.subplots()
    # TODO: keep track of nodes that are within 0.5 of each other to avoid recalculating + speed up

    draw(ax, desired_hour, is_weekend, longitudes_list, latitudes_list, colors_list, sizes_list, station_ids_list, lines, stdevs_list)
    ax.set_xlim(bbox[0], bbox[1])
    ax.set_ylim(bbox[2], bbox[3])
    ax.imshow(boston, zorder=0, extent=bbox, aspect="auto")

    def build_chart(hour):
        draw(ax, hour, is_weekend, longitudes_list, latitudes_list,
             colors_list[hour], sizes_list[hour], station_ids_list,
             lines[hour], stdevs_list[hour])

    # animator = ani.FuncAnimation(fig, buildmebarchart, interval=100)
    plt.show()


if __name__ == "__main__":
    main()

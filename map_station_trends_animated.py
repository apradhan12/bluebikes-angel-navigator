#!/usr/bin/env python3

import math
import os
import json
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from datetime import datetime
from datetime import timedelta
from geopy.distance import distance
from typing import List
import statistics
import argparse

UPPER_LEFT_CORNER = (42.4379, -71.3538)
LOWER_RIGHT_CORNER = (42.2059, -70.8148)

BBOX = (UPPER_LEFT_CORNER[1], LOWER_RIGHT_CORNER[1],
        LOWER_RIGHT_CORNER[0], UPPER_LEFT_CORNER[0])

RADIUS_MILES = 0.5
MIN_DIFF_HOUR_BIKES_DELTA = 2.5
MIN_DIFF_HOUR_POINTS = 1

# must be either True/False or False/True for now
USE_POINTS = False
SHOW_RATE_OF_CHANGE = not USE_POINTS

USE_CACHED_NEARBY_PAIRS = True


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


def draw(ax, background_img, desired_hour, is_weekend, longitudes_list, latitudes_list, colors_list, sizes_list,
         station_ids_list, lines, averages_list, stdevs_list, show_annotations):
    left, right = plt.xlim()
    bottom, top = plt.ylim()
    plt.cla()
    ax.set_xlim(left, right)
    ax.set_ylim(bottom, top)

    ax.imshow(background_img, zorder=0, extent=BBOX, aspect="auto")
    ax.scatter(longitudes_list, latitudes_list, zorder=2, alpha=1.0, c=colors_list, s=sizes_list)
    if show_annotations:
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
        r"$\mu(\mu)=%.3f$" % (sum(averages_list) / len(averages_list)),
        r"$\mu(\sigma)=%.3f$" % (sum(stdevs_list) / len(stdevs_list))))
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))


def matches_desired_weekdays(dt, is_weekend):
    if is_weekend:
        desired_days = [5, 6]
    else:
        desired_days = [0, 1, 2, 3, 4]
    return dt.weekday() in desired_days


def calculate_nearby_stations(station_ids_list, latitudes_list, longitudes_list):
    """
    Returns a list (where each element corresponds to a station) of lists of stations with a
    strictly higher ID number that are within RADIUS_MILES of the station.
    """
    nearby_stations = [[] for _ in station_ids_list]
    for i, sid1 in enumerate(station_ids_list):
        for j in range(i + 1, len(station_ids_list)):
            coords1 = (latitudes_list[i], longitudes_list[i])
            coords2 = (latitudes_list[j], longitudes_list[j])
            if distance(coords1, coords2).miles < RADIUS_MILES:
                nearby_stations[i].append(j)
                # lines.append(([coords1[1], coords2[1]], [coords1[0], coords2[0]]))
    return nearby_stations


def read_first_station_status_every_hour():
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
        # read the first file in every unique hour
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
    return all_stations


def get_aggregate_station_statistics_by_hour(all_stations, is_weekend):
    all_station_statistics = [{} for _ in range(24)]
    for station in all_stations:
        timestamp_items = list(all_stations[station].items())
        values = [[] for _ in range(24)]
        if SHOW_RATE_OF_CHANGE:  # can show values themselves, or rate of change from value to value
            for i in range(len(timestamp_items) - 1):
                first = timestamp_items[i]  # e.g. (123456789, 12)
                second = timestamp_items[i + 1]
                first_dt = datetime.fromtimestamp(first[0])
                second_dt = datetime.fromtimestamp(second[0])
                if is_one_hour_after(second_dt, first_dt):
                    if matches_desired_weekdays(first_dt, is_weekend):
                        values[first_dt.hour].append(second[1] - first[1])
                    else:
                        pass
                        # print(f"Weekday is {first_dt.weekday()} and time is {first_dt.hour}, skipping")
                else:
                    pass
                    # print(f"Timestamp delta is {second_dt - first_dt}, skipping")
        else:
            for ts_item in timestamp_items:
                dt = datetime.fromtimestamp(ts_item[0])
                if matches_desired_weekdays(dt, is_weekend):
                    values[dt.hour].append(ts_item[1])
        if any(len(hourly_values) < 2 for hourly_values in values):
            raise ValueError(f"len(values) is < 2 for id {station}")

        for hour, hourly_values in enumerate(values):
            avg = sum(hourly_values) / len(hourly_values)
            stdev = statistics.stdev(hourly_values)
            all_station_statistics[hour][station] = [avg, stdev]

    return all_station_statistics


def get_station_coords_lists(station_ids_list):
    latitudes_list = []
    longitudes_list = []
    with open("overall_stations.txt") as file_stream:
        contents = json.load(file_stream)
    for station_id in station_ids_list:
        latitudes_list.append(contents[station_id]["coords"][-1][1][0])
        longitudes_list.append(contents[station_id]["coords"][-1][1][1])
    return latitudes_list, longitudes_list


def calculate_lucrative_station_pairs(station_ids_list, latitudes_list, longitudes_list, averages_list):
    if USE_CACHED_NEARBY_PAIRS:
        try:
            with open("nearby_station_pairs.json") as file_stream:
                nearby_stations = json.load(file_stream)
        except FileNotFoundError:
            nearby_stations = calculate_nearby_stations(station_ids_list, latitudes_list, longitudes_list)
            with open("nearby_station_pairs.json", "w") as file_stream:
                json.dump(nearby_stations, file_stream)
    else:
        nearby_stations = calculate_nearby_stations(station_ids_list, latitudes_list, longitudes_list)
    lines = [[] for _ in range(24)]
    for hour in range(24):
        for i, stations_list in enumerate(nearby_stations):
            for j in stations_list:
                coords1 = (latitudes_list[i], longitudes_list[i])
                coords2 = (latitudes_list[j], longitudes_list[j])
                avg1 = averages_list[hour][i]
                avg2 = averages_list[hour][j]
                if USE_POINTS and not SHOW_RATE_OF_CHANGE:
                    surpasses_min_diff = abs(avg1 - avg2) > MIN_DIFF_HOUR_POINTS
                else:
                    surpasses_min_diff = abs(avg1 - avg2) > MIN_DIFF_HOUR_BIKES_DELTA
                if surpasses_min_diff:
                    lines[hour].append(([coords1[1], coords2[1]], [coords1[0], coords2[0]]))
    return lines


def main():
    global USE_POINTS, SHOW_RATE_OF_CHANGE

    parser = argparse.ArgumentParser()
    parser.add_argument("data_type", help="type of data to plot ('points' or 'bikes')")
    parser.add_argument("-w", "--weekend", help="show weekends", action="store_true")
    parser.add_argument("-a", "--show-annotations", help="show annotations", action="store_true")
    parser.add_argument("-s", "--single-hour", help="show only one hour", type=int)
    parser.add_argument("-i", "--interval", help="animation tick interval (ms)", type=int)
    args = parser.parse_args()
    if args.data_type not in ["points", "bikes"]:
        print('error: data_type must be one of "points", "bikes"')
        exit(2)
    USE_POINTS = args.data_type == "points"
    SHOW_RATE_OF_CHANGE = not USE_POINTS
    is_weekend = args.weekend
    single_hour = args.single_hour
    if args.interval is not None:
        interval = args.interval
    else:
        interval = 500
    show_annotations = args.show_annotations

    # read all the files in the processed_output directory to obtain timeseries data
    all_stations = read_first_station_status_every_hour()
    all_station_statistics = get_aggregate_station_statistics_by_hour(all_stations, is_weekend)

    # create a unified order for the stations, then convert dicts into lists to prepare to input into Pyplot
    station_ids_list = sorted(all_station_statistics[0].keys())
    station_statistics_list = [[hourly_stats_dict[sid] for sid in station_ids_list]
                               for hourly_stats_dict in all_station_statistics]
    averages_list: List[List[float]] = [[station_tuple[0] for station_tuple in hourly_list]
                                        for hourly_list in station_statistics_list]
    stdevs_list: List[List[float]] = [[station_tuple[1] for station_tuple in hourly_list]
                                      for hourly_list in station_statistics_list]
    colors_list = [[average_to_color(station_tuple[0]) for station_tuple in hourly_list]
                   for hourly_list in station_statistics_list]
    sizes_list = [[stdev_to_size(station_tuple[0], station_tuple[1]) for station_tuple in hourly_list]
                  for hourly_list in station_statistics_list]

    # get the station coords
    latitudes_list, longitudes_list = get_station_coords_lists(station_ids_list)
    # find station pairs
    lines = calculate_lucrative_station_pairs(station_ids_list, latitudes_list, longitudes_list, averages_list)

    boston = plt.imread("map.png")
    fig, ax = plt.subplots()

    ax.set_xlim(BBOX[0], BBOX[1])
    ax.set_ylim(BBOX[2], BBOX[3])

    def build_chart(hr):
        hr = hr % 24
        draw(ax, boston, hr, is_weekend, longitudes_list, latitudes_list,
             colors_list[hr], sizes_list[hr], station_ids_list,
             lines[hr], averages_list[hr], stdevs_list[hr], show_annotations)

    if single_hour is not None:
        print(json.dumps(sorted(
            zip([round(avg, ndigits=2) for avg in averages_list[single_hour]],
                [round(stdev, ndigits=2) for stdev in stdevs_list[single_hour]],
                station_ids_list))))
        build_chart(single_hour)
    else:
        animator = ani.FuncAnimation(fig, build_chart, interval=interval, frames=24, repeat=True)
        # animator.save("my_animation.gif", fps=10)
    plt.show()


if __name__ == "__main__":
    main()

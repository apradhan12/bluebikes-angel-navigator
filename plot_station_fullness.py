import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

ID = "5"


def process_file_contents(timestamp, contents):
    if ID in contents:
        return contents[ID]
    else:
        raise Exception(f"{ID} is not present at timestamp {timestamp}")


def main():
    timestamps = []
    valid = []
    bikes = []
    bikes_and_docks = []
    capacities = []
    points = []

    i = 0

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
        points.append(id_contents[4])
        i += 1

    end_date = datetime.combine(end_time.date(), datetime.min.time())

    # TODO: deal with inactive stations
    plt.plot(timestamps, bikes)
    plt.plot(timestamps, bikes_and_docks)
    plt.plot(timestamps, capacities)
    plt.plot(timestamps, points)

    while start_date <= end_date:
        if start_date.weekday() == 0:
            plt.axvline(x=start_date, c=(0.2, 0.2, 0.2))
        elif start_date.weekday() == 5:
            plt.axvline(x=start_date, c=(0.5, 0.5, 0.5))
            plt.axvspan(start_date, start_date + timedelta(days=2), alpha=0.5, color=(0, 1, 1))
        else:
            plt.axvline(x=start_date, c=(0.5, 0.5, 0.5))
        start_date += timedelta(days=1)

    plt.legend(["# Bikes", "# Bikes + Docks", "Capacity", "Angel Points"])
    plt.title(f"Bike capacity at Northeastern University (station ID {ID})")

    plt.xlabel("Date/Time")
    plt.axis(ymin=-3)

    plt.show()


if __name__ == "__main__":
    main()

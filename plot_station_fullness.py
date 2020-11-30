import os
import json
import matplotlib.pyplot as plt
import datetime

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

    start_time = None

    for filename in os.listdir("processed_output/"):
        with open(f"processed_output/{filename}") as file_stream:
            contents = json.load(file_stream)
            timestamp = int(filename.split(".")[0])
        if start_time is None:
            start_time = timestamp
        id_contents = process_file_contents(timestamp, contents)
        timestamps.append(datetime.datetime.fromtimestamp(timestamp))
        valid.append((0, 1, 0) if id_contents[0] else (0, 0.5, 0))
        bikes.append(id_contents[1])
        bikes_and_docks.append(id_contents[1] + id_contents[2])
        capacities.append(id_contents[3])
        points.append(id_contents[4])
        i += 1
        if i > 500:
            break

    # timestamps = [ts - start_time for ts in timestamps]

    # plt.scatter("timestamps", "bikes", data={"timestamps": timestamps, "bikes": bikes})
    plt.plot(timestamps, bikes)
    plt.plot(timestamps, bikes_and_docks)
    plt.plot(timestamps, capacities)
    plt.legend(["# Bikes", "# Bikes + Docks", "Capacity"])
    plt.title(f"Bike capacity at Northeastern University (station ID {ID})")
    # plt.scatter("timestamps", "bikes_and_docks", c="valid",
    #             data={"timestamps": timestamps, "bikes_and_docks": bikes_and_docks, "valid": valid})
    # plt.scatter("timestamps", "capacities", c="valid",
    #             data={"timestamps": timestamps, "capacities": capacities, "valid": valid})
    # plt.scatter("timestamps", "points", c="valid",
    #             data={"timestamps": timestamps, "points": points, "valid": valid})

    # data = {'a': np.arange(50),
    #         'c': np.random.randint(0, 50, 50),
    #         'd': np.random.randn(50)}
    # data['b'] = data['a'] + 10 * np.random.randn(50)
    # data['d'] = np.abs(data['d']) * 100

    # plt.plot('a', 'b', c='c', s='d', data=data)

    # plt.plot(data["a"], data["b"], 'ro')
    # plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    # plt.axis([0, 6, 0, 20])
    #
    plt.xlabel("Date/Time")
    plt.axis(ymin=0)

    plt.show()


if __name__ == "__main__":
    main()

import json
import os
from datetime import datetime


overall_stations = {}


def process_file_contents(timestamp, contents):
    if "message" in contents and contents["message"] == "Internal server error":
        print(f"Internal server error at time {timestamp}")
        return
    stations = contents["features"]
    processed = {}
    # print(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
    for station in stations:
        coords = station["geometry"]["coordinates"]
        coords.reverse()
        station_id = station["properties"]["station"]["id"]

        is_active = all(station["properties"]["station"][property_name]
                        for property_name in ["installed", "renting", "returning"])
        name = station["properties"]["station"]["name"]
        bikes = station["properties"]["station"]["bikes_available"]
        docks = station["properties"]["station"]["docks_available"]
        capacity = station["properties"]["station"]["capacity"]
        processed_entry = [is_active, bikes, docks, capacity]
        if "bike_angels" in station["properties"]:
            processed_entry.append(station["properties"]["bike_angels"]["score"])
        processed[station_id] = processed_entry

        station_entry = {
            "name": [[timestamp, name]],
            "coords": [[timestamp, coords]],
            "timestamp_added": timestamp
        }

        if station_id not in overall_stations:
            print(f"Adding station {name} ({station_id}) at time {datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            overall_stations[station_id] = station_entry
        else:
            for field_name in ["name", "coords"]:
                if overall_stations[station_id][field_name][-1][1] != station_entry[field_name][0][1]:
                    print(f"Station {name} ({station_id}) has changed its {field_name} from "
                          f"{overall_stations[station_id][field_name][-1][1]} to {station_entry[field_name][0][1]}")
                    overall_stations[station_id][field_name].append([timestamp, station_entry[field_name][0][1]])
    with open(f"processed_output/{timestamp}.txt", "w") as file_stream:
        json.dump(processed, file_stream)


def main():
    for filename in os.listdir("raw_output/"):
        if os.stat(f"raw_output/{filename}").st_size == 0:
            continue
        with open(f"raw_output/{filename}") as file_stream:
            contents = json.load(file_stream)
            timestamp = int(filename.split(".")[0])
        process_file_contents(timestamp, contents)
    with open("overall_stations.txt", "w") as file_stream:
        json.dump(overall_stations, file_stream)


if __name__ == "__main__":
    main()

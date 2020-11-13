import json
import os
import re
from datetime import datetime
from geopy.distance import distance


overall_stations = {}

EPSILON_METERS = 120
BOSTON_COORDS = [42.358056, -71.063611]
CITY_RADIUS_KM = 50


def process_file_contents(timestamp, contents):
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
        processed_entry = {
            "is_active": is_active,
            "bikes": bikes,
            "docks": docks,
            "capacity": capacity
        }
        if "bike_angels" in station["properties"]:
            processed_entry["score"] = station["properties"]["bike_angels"]["score"]
        processed[station_id] = processed_entry

        station_entry = {
            "name": name,
            "coords": coords,
            "timestamp_added": timestamp
        }

        if station_id not in overall_stations:
            print(f"Adding station {name} ({station_id}) at time {datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            overall_stations[station_id] = station_entry
        else:
            for field_name in ["name", "coords"]:
                if overall_stations[station_id][field_name] != station_entry[field_name]:
                    if field_name == "coords" and distance(coords, BOSTON_COORDS).km < CITY_RADIUS_KM < \
                            distance(overall_stations[station_id]["coords"], BOSTON_COORDS).km:
                        print(f"Station {name} ({station_id}) has changed its coordinates from "
                              f"{overall_stations[station_id]['coords']} to {station_entry['coords']}")
                        overall_stations[station_id]["coords"] = station_entry["coords"]
                    elif field_name == "coords" and distance(overall_stations[station_id]["coords"], station_entry["coords"]).m < EPSILON_METERS:
                        print(f"Station {name} ({station_id}) has changed its coordinates from "
                              f"{overall_stations[station_id]['coords']} to {station_entry['coords']} "
                              f"(distance: {distance(overall_stations[station_id]['coords'], station_entry['coords']).m} m)")
                        overall_stations[station_id]["coords"] = station_entry["coords"]
                    elif field_name == "name" and re.match("^N[0-9]+$", overall_stations[station_id]["name"]):
                        print(f"Station {name} ({station_id}) has changed its name from "
                              f"{overall_stations[station_id]['name']} to {name}")
                        overall_stations[station_id]["name"] = name
                    else:
                        print(f"Station {station_id} at timestamp {timestamp}, field {field_name} doesn't "
                              f"match earlier value at timestamp {overall_stations[station_id]['timestamp_added']}: "
                              f"{station_entry[field_name]} != {overall_stations[station_id][field_name]}")
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

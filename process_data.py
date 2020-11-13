import json
import os
from datetime import datetime


overall_stations = {}


def process_file_contents(timestamp, contents):
    stations = contents["features"]
    processed = []
    # print(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
    for station in stations:
        coords = station["geometry"]["coordinates"]
        is_active = all(station["properties"]["station"][property_name]
                        for property_name in ["installed", "renting", "returning"])
        station_id = station["properties"]["station"]["id"]
        name = station["properties"]["station"]["name"]
        if is_active:
            bike_angels_action = station["properties"]["bike_angels_action"]
            if bike_angels_action == "neutral":
                bike_angels_points = 0
            elif bike_angels_action == "take":
                bike_angels_points = station["properties"]["bike_angels_points"]
            elif bike_angels_action == "give":
                bike_angels_points = station["properties"]["bike_angels_points"] * -1
            else:
                raise ValueError(f"Bike angels action {bike_angels_action} not recognized for ID {station_id}")
            bikes = station["properties"]["station"]["bikes_available"]
            docks = station["properties"]["station"]["docks_available"]
            # print(f"Bike station {name} at {coords[0]}, {coords[1]} with id "
            #       f"{station_id} has bike angel points {bike_angels_points}")
            processed.append({
                "coords": coords,
                "is_active": is_active,
                "id": station_id,
                "bike_angels_action": bike_angels_action,
                "bike_angels_points": bike_angels_points
            })
        else:
            # print(f"Bike station {name} at {coords[0]}, {coords[1]} with id {station_id} is currently inactive")
            processed.append({
                "coords": coords,
                "is_active": is_active,
                "id": station_id
            })

        station_entry = {
            "name": name,
            "coords": coords,
            "is_active": is_active,
            "timestamp_added": timestamp
        }

        if station_id not in overall_stations:
            overall_stations[station_id] = station_entry
        else:
            for field_name in ["name", "coords", "is_active"]:
                if overall_stations[station_id][field_name] != station_entry[field_name]:
                    print(f"Station {station_id} at timestamp {timestamp}, field {field_name} doesn't "
                          f"match earlier value at timestamp {timestamp}")

def main():
    for filename in os.listdir("raw_output/")[0:1]:
        with open(f"raw_output/{filename}") as file_stream:
            contents = json.load(file_stream)
            timestamp = int(filename.split(".")[0])
            process_file_contents(timestamp, contents)


if __name__ == "__main__":
    main()
# Bluebikes Angel Navigator

Install required packages:
```
pip install -r requirements.txt
```

Plot data:
```
./plot_station_fullness.py [station ID]
```

To see each day as separate lines on the same graph, set `OVERLAY_SINGLE_DAY = True`.  
To see the legend, set `INCLUDE_LEGEND = True`.  

---

Show map data:
```
$ ./map_station_trends.py -h
usage: map_station_trends.py [-h] [-w] [-a] [-s SINGLE_HOUR] [-i INTERVAL] data_type

positional arguments:
  data_type             type of data to plot ("points" or "bikes")

optional arguments:
  -h, --help            show this help message and exit
  -w, --weekend         show weekends
  -a, --show-annotations
                        show annotations
  -s SINGLE_HOUR, --single-hour SINGLE_HOUR
                        show only one hour
  -i INTERVAL, --interval INTERVAL
                        animation tick interval (ms)
```

## Points meaning

- Positive number means that the station is almost empty (and needs bikes)
- Negative number means that the station is almost full (and needs to get rid of bikes)

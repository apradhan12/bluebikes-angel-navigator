# Bluebikes Angel Navigator

Plot data:
```
pip install -r requirements.txt
./plot_station_fullness.py [station ID]
```

To see each day as separate lines on the same graph, set `OVERLAY_SINGLE_DAY = True`.  
To see the legend, set `INCLUDE_LEGEND = True`.  

## Points meaning

- Positive number means that the station is almost empty (and needs bikes)
- Negative number means that the station is almost full (and needs to get rid of bikes)

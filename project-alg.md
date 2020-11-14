# Project

we have: 3208 datapoints for each station

each datapoint for a given station contains:
- is active? (ignore inactive datapoints)
- station coordinates, ID, name
- angel point value (consists of action + points in input dataset)
- number of bikes
- number of open docks

f: station ID, time, bikes, docks -> angel point value


first, we'll only consider previous datapoints for the same station, as well as current number of bikes and docks
- initial weights can be highest for similar times of day and the same day of the week (e.g. for 4:00 p.m. on a Saturday, 3:45 p.m. and 3:30 p.m. are weighted highly, as well as 3:30-4:30 p.m. the previous Saturdays)
- produce a scalar
- we have a vector of the current number of docks, bikes, plus previous 3208 values (set to 0 if absent)
- we want to determine the weight vector
- domain has 3210 dimensions, codomain has 1 dimension
- we have 3208 points
- the function is affine (if all the previous datapoints are 0s, the resulting point value can be nonzero)

- problem: might not be affine linear - logistic curve makes more sense for correspondence from bike/docks ratio to angel points

- we need to use neural networks

## Data collected 2020-11-13

Visited a total of 3 bike stations

1. Ruggles - 0 bikes, 17 docks, 18 capacity (according to app)
    - there was 1 bike (whose dock had a *blinking* light) and 17 empty docks
    - the 1 bike in the station was not showing up on the app
    - when I requested to take out a bike, it got stuck on loading for several seconds
    - I could not remove the bike
2. Avenue Louis Pasteur at Longwood Ave - 22 bikes, 1 dock, 25 capacity (according to app)
    - one of the occupied docks had a *blinking* red light
    - there were 24 total bikes and 1 empty dock
    - although the system registered `capacity - (bikes + dock) = 2`, I only observed an issue with one of the bikes/docks
    - I was able to take out a bike, but not the one with the blinking light
    - moving a bike to the empty dock did not affect the problem
3. Comm Ave at Agganis Way - 8 bikes, 6 docks, 15 capacity (according to app)
    - one of the occupied docks had a *solid* red light
    - there were 9 total bikes and 6 empty docks
    - I could not take out the bike whose dock had a solid light
    - I could not press the "request repairs" button until I took out a bike and returned it
    - this immediately marked the dock as solid red, and sent me an email with a Google Form link asking about the problem with the bike

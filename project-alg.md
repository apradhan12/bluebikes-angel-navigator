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

interesting features/questions:
- period/amplitude of oscillation (if any)
- movements "against the trend" (e.g. taking out a bike when most people are adding bikes)
- what are the busiest times of day for each station?
- is there any statistical difference between weekdays/weekends for a given station?
- is the derivative any easier to predict than the function itself?
- what are the most and least predictable times of day/days of the week?

additional features:
- highlight areas where angel points are nonzero / # bikes is below/above a certain threshold
- moving average
- split data into days, plot days on top of each other

noticings:
- Northeastern typically dips weekend afternoons whereas MIT typically goes up

## More questions 12-6-2020

- When are the stations near me in greatest need? (both in terms of points *and* rate of change in bike station fullness - hopefully these two are strongly correlated)
- If I want to get Angel Points when I go to/from work, which station do I need to go to, and how should I adjust my commute time?
- If I want to make sure I always have a bike when I want to go somewhere around a particular time, which station(s) and time(s) are my safest bet?
- As the system moves forward from a given state, with what level of confidence do we know its output (as a function of elapsed time and start time)?
---
- At any given time, the best short-term strategy for collecting points is to go to a pair of stations close to each other with a large point difference.
- Which of these pairs will give me the most points as I bike?
    - during the course of the hour following the start of my point-gathering, what is the average rate of change of bikes at these two stations?
    - what is the capacity of each of the stations?
---
- Even if we can't create paths for people, we can at least point them to the best pairs
- plot a map for average # of angel points at a given time/weekday - this will help inform the problem
- draw lines between stations with a high point differential and a low distance between them
---
- Is the rate of change of bikes in a *normal distribution*?
- How predictable is the rate of change of bikes compared to the number of points?
    - probably will use normal distribution CDF (phi) for this
- Does the stdev of the number of points go down when you only allow similar point values?

Things to do:
- animate the graph to see values over time (git stashed)
- only show data points where the number of bikes was within some small margin of the first reading
    - this will give us a sense of how accurate a [neural network algorithm for angel points] might be that takes into account only bikes and time/weekday
---
- ~~add print statements w/ list of averages and stdevs if you do a single hour~~
- allow bikes, or rate of change of points (also, ratios of bikes to capacity, i.e. percent full?)
- try with only within epsilon of number of bikes on the first day
- clean up constants - don't use constants for things that aren't really constant
- fix the 2.5 vs 1 difference ratio for bike rate of change compared to points
    - isn't yet accounted for in the minimum threshold for larger points

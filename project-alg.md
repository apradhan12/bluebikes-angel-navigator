# PROJECT

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

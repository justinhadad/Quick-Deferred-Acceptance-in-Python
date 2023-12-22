# Quick-Deferred-Acceptance-in-Python

This program (.py and .ipynb) generates stable matches (one-to-one) for autogenerated markets with uncorrelated preferences.

Matches are women-indexed, i.e. are in the format (woman, man). Values are drawn randomly from the uniform distribution [0,1]. Women's values are a 2D nupmy array where [i,j] is woman i's value for man j; men's values are a 2D numpy array where [i,j] is man i's value for woman j. 

The program demonstrates, for randomly generated values, statistics on (1) regular MPDA, (2) the group-optimal truncation, (3) the gains from group-optimal truncation (aka WPDA),  (4) the gains from an extra man in the market, and (5) the gains from the worst-off woman leaving the market. These can be made trivially analagous to real-world scenarios.

"Single Iteration with Steps.py" prints the series of proposals with the above statistics. "Single Iteration.py" returns average rank results in MPDA and WPDA.

Values created using uniform iid numpy arrays and can be easily transformed.

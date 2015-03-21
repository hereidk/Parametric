Parametric
==========

Calculate losses from historical hurricane/earthquake frequency, user-defined payout structure

IBTrACS = Historical hurricane tracks
USGS = Historical earthquakes, >=M6.0, live feed

Define extent of payout box using .csv file with Lat/Lon.  If box is not closed, point is added to close automatically.

GUI gets user input on payout structure - average annual loss, loss costs returned in same units as user input.
Payout structure based on earthquake magnitude ranges or hurricane wind speed category (Saffir-Simpson).

Main file is ParamMain, class definition in ParamBox.

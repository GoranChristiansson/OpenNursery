# OpenNursery
Software for running a small scale tree nursery

v0.1, 2021-05-03 Vince Busch, Goran Christiansson/Trees for Peace Foundation - a collection of software tools that we developed for our nut tree nursery.
Feel free to use and share alike. The first publicly shared sourcecode in May 2021 is rough, but works for us. At some point of time in the future, we will release a new version that is easier to customize for your plant nursery.


## Entomatic
The "entomatic" is a "hot callus pipe system" for heating grafted trees, using an Arduino for each "bench" with two pipes on each bench. The EntBerry software runs on a data collecting/logging/visualization computer (we used a Raspberry Pi 3 for this, any computer with python/influxdb works). 


## Inventory
Here is a collection of python scripts that keep track of the MainInventory file, and generates unique EU-approved labels for each tree. 
The labels are generated for two kinds of label printers: Dymo LabelWriter 450 and Citizen Labelprinter CL-S621II.
We have optional QR-code and GPS-position-collection for each individual tree, so that we can build an open-source geographic genetic library of trees.



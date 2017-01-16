# Bluetooth_RSSI_vs_Distance

Synopsis
--------

Written specifically for the Galileo Board, this program was used to experimentally determine the relationship between rssi values and distance.

The program prompts the user for a distance value, and then the program will scan for a hard-coded mac address for a hard-coded number of times (lines 131 and 133), reading in the rssi value each time. The reason why the mac address and the number of scans were hard-coded was so that the program would require fewer user inputs and would run faster. 

The program will save the data to multiple text files. It saves distance vs average rssi value, distance vs minimum rssi value, distance vs maximum rssi value, distance vs total number of seconds between packets, distance vs list of timestamps. 

The program will save the data and quit when the user enters any non-digit character when prompted for a distance value. 

Motivation
----------

To determine how reliable rssi values are for determining the distance between two bluetooth devices (not that reliable...)

Installation
------------

You will need to run this program from the Intel Galileo Board and make sure that the Galileo Board has the pybluez python module. 


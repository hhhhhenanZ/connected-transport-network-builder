# Pls install osm2gmns 1.0.1 package
# Use this pip command: pip install osm2gmns==1.0.1
# Reference: https://pypi.org/project/osm2gmns/1.0.1/


import csv
import os
import osm2gmns as og


def osm2gmns_network():

    input_file = r"data/Tempe.osm" # Update this file name to match your osm
    # option 1: for urban networks
    net = og.getNetFromFile(input_file, link_types=('motorway','trunk','primary','secondary','tertiary'))
    # option 2: for rural networks
    #net = og.getNetFromFile(input_file, link_types=('motorway','trunk','primary','secondary','residential','tertiary'))

    # Consolidate intersections and fill default values
    og.consolidateComplexIntersections(net, auto_identify=True)
    og.fillLinkAttributesWithDefaultValues(net, default_lanes=True, default_speed=True, default_capacity=True)
    og.generateNodeActivityInfo(net)

    # Output the processed network
    og.outputNetToCSV(net)
    
#main program
osm2gmns_network()

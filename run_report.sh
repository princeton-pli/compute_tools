#!/bin/bash

FILEPATH=cluster_stats.txt

shownodes -p pli > $FILEPATH
python visualize_cluster_usage.py $FILEPATH

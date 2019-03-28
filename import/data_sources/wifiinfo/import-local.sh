#!/bin/bash

set -xue

python data_sources/wifiinfo/models.py

python data_sources/trafficorder/copy_to_model.py 

#!/bin/bash

# Change directory to build
cd build

# Run cmake with Debug build type
cmake -DCMAKE_BUILD_TYPE=Release ../src

# Run make to build the project
make

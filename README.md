
# ARGoS Simulation

## Citation

C. Pinciroli, M.S. Talamali, A. Reina, J.A.R. Marshall and V.Trianni. Simulating Kilobots within ARGoS: models and experimental validation. In _Proceedings of 11th International Conference on Swarm Intelligence (ANTS)_, LNCS 11172: 176-187, Springer, Cham, 2018. doi: [10.1007/978-3-030-00533-7_14](https://doi.org/10.1007/978-3-030-00533-7_14)

## Compiling the code

Make sure you have ARGoS >= 3.0.0-beta52 installed!

Commands:
```shell
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ../src
make
sudo make install
```
## Before Running the Simulation
These folders need to be created for the robots to output their data
```shell
mkdir robot_color_output
mkdir sensor_color_output
mkdir time_output
```
## Run the ARGoS Simulation
```shell
argos3 -c src/examples/experiments/my_kilobot_movement.argos
```

Each robots outputs its color opinion at every timestep in a txt file in the ``robot_color_output`` folder.
# Multi-Agent Simulation
The code for the MA Simulation can be found in the ```MA-Simulation``` folder.
A small readme is added there on how to execute it.
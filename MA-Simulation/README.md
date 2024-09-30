## Multi-Agent Simulation

To run the MA Simulation, you can run the [```main.py```](main.py) file.<br/>
You can change the conguration of the run (the parameters like sensor noise, 
communication nosie, etc.) from the [```config.yaml```](config.yaml) file. <br/>
It is also possible to run the simulation for all combinations of sensor noise, commnunication noise
and personal information weight at once. For this change the ```all_parameters_run``` 
to 1 (or anything else except for 0) in the [```config.yaml```](config.yaml) file.<br/>

The output from the simulation will be stored in the ```output_data``` folder as ``output_run*.txt`` files.
There will be one file for each independent run. It stores the number of robots commited to each color at a every timestep.

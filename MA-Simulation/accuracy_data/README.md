## How to get the accuracy data

First modify the code to make it a non-switching environment (```main.py```)
for this in ```run_simulation_all()``` the color switching line should look like:
```if t % config['color_change_timestep'] == 0 and number_of_color_switches < 1```.<br/> Also
uncomment the few lines in ```plot_graphs.py``` in ```execute_and_plot()```
function to generate the average_quality_ir*.txt file which is good for generating speed data
later. Now run simulations to create data (or just copy the data from here).

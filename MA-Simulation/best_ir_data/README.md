## How to generate best IR heatmap 

Here we are creating a heatmap that will show the best informed ratio for a given
personal info weight and communication noise.<br/>
<br/>
Move data from the fixed_sensor_data folder for all ir for a fixed sensor noise into
the output_data folder. Run the ```best_ir_accuracy_csv_maker.py```, this will create
a csv file in the best_ir_data folder. Then run the ```create_best_ir_heatmap_from_csv.py```,
this will create the heatmap.
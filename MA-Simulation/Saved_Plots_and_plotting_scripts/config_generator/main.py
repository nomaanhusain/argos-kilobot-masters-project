from datetime import datetime
import numpy as np

conf_file_name = 'ASB_experiment_G40_conf5'
#0.4 sn setting
# option_1_quality = 256
# option_2_quality = 107
# option_3_quality = 107
# option_4_quality = 107
# option_5_quality = 107

#0.5 sn
# option_1_quality = 200
# option_2_quality = 121
# option_3_quality = 121
# option_4_quality = 121
# option_5_quality = 121

option_1_quality = 117
option_2_quality = 117
option_3_quality = 117
option_4_quality = 117
option_5_quality = 216

# 412 maj, 68 min 

wall_value = 42

module_grid = np.zeros((10, 20), dtype=np.uint8)
cell_grid = np.zeros((20, 40), dtype=np.uint8)
# print(cell_grid)


def make_walls(grid):
  grid[:, 0:11] = wall_value
  grid[:, -1:] = wall_value
  grid[0:1, :] = wall_value
  grid[-1:, :] = wall_value
  # print("grid wall", grid)
  return grid


def distribute_tiles(grid):
  print("Distribute Grid")
  op1 = np.ones((option_1_quality, )) * 1
  op2 = np.ones((option_2_quality, )) * 2
  op3 = np.ones((option_3_quality, )) * 3
  op4 = np.ones((option_4_quality, )) * 4
  op5 = np.ones((option_5_quality, )) * 5

  # print("op3= ",op3)

  op = np.concatenate((op1, op2, op3, op4, op5))


  np.random.shuffle(op)
  print("op")
  print(op)
  print("--------")
  op = np.reshape(op, (18, 38))
  grid[1:19, 1:39] = op
  print(grid)
  return grid


if __name__ == "__main__":

  # set up module grid
  module_grid = make_walls(module_grid)

  # set up cell grid
  cell_grid = distribute_tiles(cell_grid)

  # write file
  with open(conf_file_name + '.kconf', 'w') as f:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print('# Experiment: ', conf_file_name, file=f)
    print('# Generation Time: ', dt_string, file=f)
    print('\n', file=f)


    # writing for each module
    for x in range(10):
      for y in range(20):
        # print header
        print('address', file=f)
        print('module:' + str(x) + '-' + str(y) + '\n', file=f)
        print('data', file=f)
        # fill with values ..
        print(hex(x), file=f)
        print(hex(y), file=f)

        #  if (x == 0) or (x == 9):
        #    print(hex(42), file=f)
        #    print(hex(cell_grid[x * 2, y * 2 + 1]), file=f)
        #   print(hex(cell_grid[x * 2 + 1, y * 2 + 1]), file=f)
        # print(hex(cell_grid[x * 2, y * 2]), file=f)
        # print(hex(cell_grid[x * 2 + 1, y * 2]), file=f)

        # elif (x == 1 and y == 0) or (x == 1 and y == 19) or (x == 2 and y == 0) or (x == 2 and y == 19) or (
        #        x == 3 and y == 0) or (x == 3 and y == 19) or (x == 4 and y == 0) or (x == 4 and y == 19) or (
        #        x == 5 and y == 0) or (x == 5 and y == 19) or (x == 6 and y == 0) or (x == 6 and y == 19) or (
        #        x == 7 and y == 0) or (x == 7 and y == 19) or (x == 8 and y == 0) or (x == 8 and y == 19):
        #    print(hex(42), file=f)

        #else:
        #NOTE: This multiplication by 2 is like a translation of the 20x40 grid into a 10x20 grind in a way
        if ((cell_grid[x * 2, y * 2 + 1]) == 0):
          print(hex(42), file=f)

        elif ((cell_grid[x * 2 + 1, y * 2 + 1]) == 0):
          print(hex(42), file=f)

        elif ((cell_grid[x * 2, y * 2]) == 0):
          print(hex(42), file=f)

        elif ((cell_grid[x * 2 + 1, y * 2]) == 0):
          print(hex(42), file=f)
        else:
          print(hex(module_grid[x, y]), file=f)

  #        print(hex(module_grid[x, y]), file=f)
  #print(hex(cell_grid[x * 2, y * 2]))
        print(hex(cell_grid[x * 2, y * 2 + 1]), file=f)
        print(hex(cell_grid[x * 2 + 1, y * 2 + 1]), file=f)
        print(hex(cell_grid[x * 2, y * 2]), file=f)
        print(hex(cell_grid[x * 2 + 1, y * 2]), file=f)

        # needed for structure
        print('', file=f)

# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "Debug")
  file(REMOVE_RECURSE
  "examples/behaviors/CMakeFiles/move_and_talk_autogen.dir/AutogenUsed.txt"
  "examples/behaviors/CMakeFiles/move_and_talk_autogen.dir/ParseCache.txt"
  "examples/behaviors/move_and_talk_autogen"
  "examples/loop_functions/colorful_floor_loop_function/CMakeFiles/colorful_floor_loop_function_autogen.dir/AutogenUsed.txt"
  "examples/loop_functions/colorful_floor_loop_function/CMakeFiles/colorful_floor_loop_function_autogen.dir/ParseCache.txt"
  "examples/loop_functions/colorful_floor_loop_function/colorful_floor_loop_function_autogen"
  "plugins/robots/kilobot/CMakeFiles/argos3plugin_simulator_kilobot_autogen.dir/AutogenUsed.txt"
  "plugins/robots/kilobot/CMakeFiles/argos3plugin_simulator_kilobot_autogen.dir/ParseCache.txt"
  "plugins/robots/kilobot/CMakeFiles/argos3plugin_simulator_kilolib_autogen.dir/AutogenUsed.txt"
  "plugins/robots/kilobot/CMakeFiles/argos3plugin_simulator_kilolib_autogen.dir/ParseCache.txt"
  "plugins/robots/kilobot/argos3plugin_simulator_kilobot_autogen"
  "plugins/robots/kilobot/argos3plugin_simulator_kilolib_autogen"
  )
endif()

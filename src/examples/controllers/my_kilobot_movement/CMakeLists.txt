add_library(my_kilobot_movement SHARED my_kilobot_movement.h my_kilobot_movement.cpp)
target_link_libraries(my_kilobot_movement
        argos3core_simulator
        argos3plugin_simulator_kilobot
        argos3plugin_simulator_genericrobot)
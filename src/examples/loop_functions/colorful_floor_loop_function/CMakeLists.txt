include_directories(${ARGOS_QTOPENGL_INCLUDE_DIRS})
add_library(colorful_floor_loop_function MODULE
            colorful_floor_loop_function.cpp
            colorful_floor_loop_function.h)
target_link_libraries(colorful_floor_loop_function
        argos3core_simulator
        argos3plugin_simulator_entities
        argos3plugin_simulator_kilobot
        argos3plugin_simulator_qtopengl
        ${ARGOS_QTOPENGL_LIBRARIES})

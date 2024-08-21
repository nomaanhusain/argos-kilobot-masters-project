# If Qt+OpenGL dependencies were found, descend into these directories
if(ARGOS_QTOPENGL_FOUND)
#  add_subdirectory(debug_loop_functions)
#  add_subdirectory(trajectory_loop_functions)
  add_subdirectory(colorful_floor_loop_function)
#  add_subdirectory(aust_loop_function)
#  add_subdirectory(zakir_loop_function)
endif(ARGOS_QTOPENGL_FOUND)

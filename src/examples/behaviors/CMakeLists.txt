if(ARGOS_BUILD_FOR_SIMULATOR)
  include_directories(${CMAKE_SOURCE_DIR}/plugins/robots/kilobot/control_interface)

  add_executable(move_and_talk move_and_talk.h move_and_talk.c)
  target_link_libraries(move_and_talk argos3plugin_simulator_kilolib)

endif(ARGOS_BUILD_FOR_SIMULATOR)

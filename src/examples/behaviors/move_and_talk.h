//
// Created by nomaan on 8/12/24.
//

#ifndef MOVE_AND_TALK_H
#define MOVE_AND_TALK_H

#ifdef ARGOS_simulator_BUILD

#ifdef __cplusplus /* If this is a C++ compiler, use C linkage */
extern "C" {
#endif

    ////////////////////////////////////////
    // DEBUGGING INFORMATION
    //
    // You must define a struct called 'debug_info_t'
    //kilo_message_tx_success
    // The name 'debug_info_t' is mandatory
    // The content of the struct is whatever you want
    typedef struct {
        int received_message;
    } debug_info_t;
    //
    ////////////////////////////////////////

#ifdef __cplusplus /* If this is a C++ compiler, use C linkage */
}
#endif

#endif // ARGOS_simulator_BUILD


#endif //MOVE_AND_TALK_H

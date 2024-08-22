//
// Created by nomaan on 8/12/24.
//
#include <kilolib.h>
#include <move_and_talk.h>
#include <debug.h>
#include <time.h>

int message_sent = 0;
message_t message;
uint32_t last_message_sent_tick = 0;
const int interval = 100; // Interval of 64 kiloticks

int new_message = 0;
int distance = 0;
uint16_t sender_id = -1;

int received_message_data = -1;
uint8_t received_color = 0;
// int rand_num = 0;

void setup()
{
}

void loop()
{
    // uint8_t ground_color = get_ambientlight();
    // Toggle even/odd message every 64 clock ticks (roughly 2 seconds).
    // if (kilo_ticks > last_message_sent_tick + 100)
    // {
    //     last_message_sent_tick = kilo_ticks;
    //
    //     if (received_message_data == 0)
    //     {
    //         message.type = NORMAL;
    //         message.data[0] = 0;
    //         message.data[1] = kilo_uid;
    //         // message.data[2] = 0;
    //         message.crc = message_crc(&message);
    //
    //         // Update odd for next time.
    //         received_message_data = 1;
    //     }
    //     else
    //     {
    //         message.type = NORMAL;
    //         message.data[0] = 1;
    //         message.data[1] = kilo_uid;
    //         // message.data[2] = ground_color;
    //         message.crc = message_crc(&message);
    //
    //         // Update odd for next time.
    //         received_message_data = 0;
    //     }
    // }
    //
    // // Blink the LED magenta whenever a message is sent.
    // if (message_sent)
    // {
    //     message_sent = 0;
    //
    //     // set_color(RGB(1, 0, 1));
    //     // delay(100);
    //     // set_color(RGB(0, 0, 0));
    // }
    //
    // if (new_message == 1)
    // {
    //     new_message = 0;
    //     debug_print("message received from %d. Kilo Tick %d, received color = \n",sender_id, kilo_ticks);
    //
    //     // Near ...
    //     if (distance <= 100)
    //     {
    //         // ... and even: set the LED red.
    //         if (received_message_data == 0)
    //         {
    //             set_color(RGB(1, 0, 0));
    //         }
    //         // Message of impotance is received here.
    //         else
    //         {
    //             debug_print("Green message received from %d. Kilo Tick %d, received color = \n",sender_id, kilo_ticks);
    //             set_color(RGB(0, 1, 0));
    //         }
    //     }
    //
    //     // Wherever you are: set LED off after 100 ms to achieve blink effect.
    //     delay(100);
    //     set_color(RGB(0, 0, 0));
    // }

    // delay(100);



    //DO the movement
     // Set the LED green.
     // set_color(RGB(0, 1, 0));
     // Spinup the motors to overcome friction.
     spinup_motors();
     // Move straight for 2 seconds (2000 ms).
     set_motors(kilo_straight_left, kilo_straight_right);
     delay(2000);

     // Set the LED red.
     // set_color(RGB(1, 0, 0));
     // Spinup the motors to overcome friction.
     spinup_motors();
     // Turn left for 2 seconds (2000 ms).
     set_motors(kilo_turn_left, 0);
     delay(2000);

     // Set the LED blue.
     // set_color(RGB(0, 0, 1));
     // Spinup the motors to overcome friction.
     spinup_motors();
     // Turn right for 2 seconds (2000 ms).
     set_motors(0, kilo_turn_right);
     delay(2000);

     // Set the LED off.
     // set_color(RGB(0, 0, 0));
     // Stop for half a second (500 ms).
     // set_motors(0, 0);
     // delay(500);
}

// message_t *message_tx()
// {
//     return &message;
// }
//
// void message_tx_succes()
// {
//     message_sent = 1;
// }
// void message_rx(message_t *message, distance_measurement_t *distance_measurement)
// {
//     // Set flag on message reception.
//     new_message = 1;
//
//     distance = estimate_distance(distance_measurement);
//     received_message_data = message->data[0];
//     sender_id = message->data[1];
//     // received_color = message->data[2];
//
// }

int main()
{
    kilo_init();
    // srand(time(NULL));
    // rand_num = rand() % 50 + 1;
    // debug_print("Main function. Kilo Ticks = %d \n", kilo_ticks);
    // kilo_message_tx = message_tx;
    // kilo_message_tx_success = message_tx_succes;
    // kilo_message_rx = message_rx;
    debug_info_create();
    kilo_start(setup, loop);

    return 0;
}

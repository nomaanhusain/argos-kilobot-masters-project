//
// Created by nomaan on 8/12/24.
//
#include <kilolib.h>
#include <move_and_talk.h>
#include <debug.h>
#include <time.h>
#include <math.h>

/*-----------------------------------------------------------------------------------------------*/
/* Define section here you can define values, e.g., messages types                               */
/*-----------------------------------------------------------------------------------------------*/
// options
#define UNCOMMITTED 99  //opinion for uncommitted
// message types
#define FROMBOT 9  //the message is from robot and not kilogrid
#define INIT_MSG 10  // initial message from the kilogrid
#define GRID_MSG 11  // info msg from the kilogrid with option and position
#define VIRTUAL_AGENT_MSG 12  // msg forwarded from the kilogrid
#define TO_KILOGRID_MSG 62
#define min(a,b) ((a) < (b) ? a : b)
#define INFOPTION (0)
#define SWARMSIZE 100
//#define AGENTS_PER_GROUP 20
//#define GROUPS 5
#define MSG_KILOG 1
#define MSG_NEIGHBOUR 1

#define kval 0 //0 all majority

#define OMG 0.25
#define ALPHA 0.2
#define INFORMED 1
/*-----------------------------------------------------------------------------------------------*/
/* Change these when running experiment                                                          */
/*-----------------------------------------------------------------------------------------------*/
//double noise = 0.99; // SET THIS TO -1 FOR NO NOISE, 0.1--> 0.05, 0.5-->0.25
/*-----------------------------------------------------------------------------------------------*/

//opinion = A -->1   //opinion = B --> 2  //uncommited = C --> UNCOMITTED
int currentopinion; //1

double timer; // to hold time to be in each state
double avg_exploration_time = 800.0; //***--> time to be in exploration state--> fixed
//double avg_uncommitted_time = 200.0; // time to stay in dissemination for uncommitted agents
///double dissemparam = 1300.0;

int foundmodules[18][38] = {0}; //to keep track of tiles visited in one exploration cycle


int estimateR;
int estimateB;
int estimateG;
int estimateY;
int estimateBL;
int estimateN;

int avg_neighbours;


int tot_e;

/*-----------------------------------------------------------------------------------------------*/
/* Enum section - here we can define useful enums                                                */
/*-----------------------------------------------------------------------------------------------*/
typedef enum{
    false = 0,
    true = 1,
} bool;

/* Enum for different motion types */
typedef enum {
    STOP = 0,
    FORWARD,
    TURN_LEFT,
    TURN_RIGHT,
} motion_t;

/* Enum for different states */
typedef enum {
    EXPLORATION,
    FILTER,
} state;
/* Enum for different wall function  states */
typedef enum {
    TURN_TO_AVOID_WALL,
    STRAIGHT_TO_AVOID_WALL,
    COMPLETE_WALL_AVOIDANCE,
} wall_state;
/*-----------------------------------------------------------------------------------------------*/
state current_state = EXPLORATION;
wall_state wall_function_state = TURN_TO_AVOID_WALL;
/*-----------------------------------------------------------------------------------------------*/
/* Motion related Variables                                                                      */
/*-----------------------------------------------------------------------------------------------*/
motion_t current_motion_type = STOP;
unsigned int turning_ticks = 0;
const uint8_t max_turning_ticks = 150; //*** constant to set maximum rotation to turn during random walk
const uint32_t max_straight_ticks = 300; //*** set the time to walk straight before randomly turning
const uint8_t max_wall_avoidance_turning_ticks = 130;
const uint32_t max_wall_avoidance_straight_ticks = 260;
//const uint32_t broadcast_ticks = 32;
uint32_t last_motion_ticks = 0;
uint32_t last_motion_wall_ticks = 0;

uint8_t kilogrid_commitment = 0;  // This is the initial commitment attained from kilogrid
//float my_commitment_quality = 0.0;
int last_changed = 0;
bool wall_avoidance_turning = false;
bool wall_avoidance_straight = false;

int model = 1;

/*-----------------------------------------------------------------------------------------------*/
/* Communication variables - used for communication and stuff                                    */
/*-----------------------------------------------------------------------------------------------*/
bool broadcast_msg = false;
#define MSG_SEND_TRIES 1
// Kilobot -> Kilogrid
uint32_t msg_counter_sent = MSG_SEND_TRIES + 1;  // counts the messages sent
uint32_t msg_number_send = 0;  // change if you want to send a msg
uint32_t msg_number_current_send = 0;  // var for checking against the last
// Kilogrid -> Kilobot
bool init_flag = false;
bool received_grid_msg_flag = false;
bool received_virtual_agent_msg_flag = false;

int op_message_env_voter = 0;
int op_message_neighbour_voter = 0;
// Flag to keep track of new messages.
message_t message;
int new_message = 0;

int last_changed;
// Flag to keep track of message transmission.
int message_sent = 0;

int storeid[SWARMSIZE] = {};

int received_option; //to save an opinion received from another bot
int received_option_kilogrid; // to save option received from kilogrid
int received_uid; //previously used to save neighbours kilouid temporarily
int wall_flag; //to check if wall signal or not
/*-----------------------------------------------------------------------------------------------*/
/* Arena variables                                                                               */
/*-----------------------------------------------------------------------------------------------*/

bool hit_wall = false;  // set to true if wall detected
bool wall_avoidance_state = false;
//to keep track of tiles and quality
int total_tiles_found;
int tiles_of_1_option;
int tiles_of_2_option;
int tiles_of_3_option;
int tiles_of_4_option;
int tiles_of_2_option;
int tiles_of_5_option;


int op_count[5] = {0, 0, 0, 0, 0};
int op_count_vm[5] = {0, 0, 0, 0, 0};

//Storing color opions of neighbours and their ids
#define MAX_COLOR_OPINIONS 5
#define NUM_OF_NEIGHBOURS 5
double decision_arr[MAX_COLOR_OPINIONS];
typedef struct {
    int color_opinion;  // The color opinion
    int count;          // Count of how many neighbors share this opinion
} ColorOpinion;

typedef struct {
    ColorOpinion opinions[MAX_COLOR_OPINIONS];
    int size;  // Current number of unique color opinions
} ColorHashSet;

typedef struct {
    int uids[NUM_OF_NEIGHBOURS];
    int size;  // Current number of unique robot UIDs
} UIDHashSet;

// Add a color opinion to the hashset
void add_color_opinion(ColorHashSet* set, int color) {
    for (int i = 0; i < set->size; i++) {
        if (set->opinions[i].color_opinion == color) {
            set->opinions[i].count++;
            return;
        }
    }

    // If color not found, add a new entry
    if (set->size < MAX_COLOR_OPINIONS) {
        set->opinions[set->size].color_opinion = color;
        set->opinions[set->size].count = 1;
        set->size++;
    }
}
int get_color_opinion_count(ColorHashSet* set, int color) {
    for(int i=0; i< set->size; i++) {
        if(set->opinions[i].color_opinion == color) {
            return  set->opinions[i].count;
        }
    }
    return 0;
}

// Check if the UID already exists in the set
int uid_exists(UIDHashSet* set, int uid) {
    for (int i = 0; i < set->size; i++) {
        if (set->uids[i] == uid) {
            return 1;
        }
    }
    return 0;
}
// Add a UID to the UID hashset
int add_uid(UIDHashSet* set, int uid) {
    if (!uid_exists(set, uid) && set->size < NUM_OF_NEIGHBOURS) {
        set->uids[set->size] = uid;
        set->size++;
        return 1;
    }
    return 0;
}

// Function to clear the color hashset
void clear_color_hashset(ColorHashSet* set) {
    set->size = 0;  // Reset the size to 0, effectively clearing the set
}

// Function to clear the UID hashset
void clear_uid_hashset(UIDHashSet* set) {
    set->size = 0;  // Reset the size to 0, effectively clearing the set
}

// Function to print the current state of the color opinions
void print_color_opinions(ColorHashSet* set) {
    for (int i = 0; i < set->size; i++) {
        printf("Kiloid = %d Color: %d, Count: %d\n", kilo_uid, set->opinions[i].color_opinion, set->opinions[i].count);
    }
}

ColorHashSet colorSet = {.size = 0};
UIDHashSet uidSet = {.size = 0};
int opinion_receive_start_time = 0;

/*-----------------------------------------------------------------------------------------------*/
/* Setting the Motion of the Bot                                                                 */
/*-----------------------------------------------------------------------------------------------*/
void set_motion( motion_t new_motion_type ) {
    if( current_motion_type != new_motion_type ){

        switch( new_motion_type ) {
            case FORWARD:
                spinup_motors();
            set_motors(kilo_straight_left,kilo_straight_right);
            break;
            case TURN_LEFT:
                spinup_motors();
            set_motors(kilo_turn_left,0);
            break;
            case TURN_RIGHT:
                spinup_motors();
            set_motors(0,kilo_turn_right);
            break;
            case STOP:
                set_motors(0,0);
            break;
        }
        current_motion_type = new_motion_type;
    }
}

/*-----------------------------------------------------------------------------------------------*/
/* Function to get a random 1 or 0 to check for self-sourced noise or social interaction         */
/*-----------------------------------------------------------------------------------------------*/
double r2()
{
    return (double)rand() / (double)RAND_MAX ;
}


/*-----------------------------------------------------------------------------------------------*/
/*                          The Polling Function- Social interaction                             */
/*                                                                                               */
/*-----------------------------------------------------------------------------------------------*/
void poll(){


    if (model == 0) {

        int array_size = sizeof(op_count) / sizeof(op_count[0]);
        int max_sum_index = 0;
        int all_same_or_zero = 1; // Flag to check if all numbers are same or zero
        int max_count = 0; // Maximum value found so far

        // Find the maximum value in the array
        for (int i = 0; i < array_size; i++) {
            if (op_count[i] > max_count) {
                max_count = op_count[i];
            }
        }

        // Check if all numbers are the same or zero
        for (int i = 1; i < array_size; i++) {
            if (op_count[i] != op_count[0]) {
                all_same_or_zero = 0;
                break;
            }
        }

        // If all numbers are the same or zero, choose one index randomly
        if (all_same_or_zero) {
            srand(time(NULL)); // Seed the random number generator
            max_sum_index = rand() % array_size; // Choose a random index
        } else {
            // Find the indexes with the highest value
            int indexes[array_size];
            int count = 0;
            for (int i = 0; i < array_size; i++) {
                if (op_count[i] == max_count) {
                    indexes[count++] = i;
                }
            }
            srand(time(NULL)); // Seed the random number generator
            max_sum_index = indexes[rand() % count]; // Choose one of the indexes randomly
        }



        currentopinion= max_sum_index + 1;
        //printf("THE UPDATED OPINION I  %d \n ", currentopinion);





    }else { //for voter rule
        int array_size = sizeof(op_count_vm) / sizeof(op_count_vm[0]);
        int max_sum_index = 0;
        int all_same_or_zero = 1; // Flag to check if all numbers are same or zero
        int max_count = 0; // Maximum value found so far

        // Find the maximum value in the array
        for (int i = 0; i < array_size; i++) {
            if (op_count_vm[i] > max_count) {
                max_count = op_count_vm[i];
            }
        }

        // Check if all numbers are the same or zero
        for (int i = 1; i < array_size; i++) {
            if (op_count_vm[i] != op_count_vm[0]) {
                all_same_or_zero = 0;
                break;
            }
        }

        // If all numbers are the same or zero, choose one index randomly
        if (all_same_or_zero) {
            srand(time(NULL)); // Seed the random number generator
            max_sum_index = rand() % array_size; // Choose a random index
        } else {
            // Find the indexes with the highest value
            int indexes[array_size];
            int count = 0;
            for (int i = 0; i < array_size; i++) {
                if (op_count_vm[i] == max_count) {
                    indexes[count++] = i;
                }
            }
            srand(time(NULL)); // Seed the random number generator
            max_sum_index = indexes[rand() % count]; // Choose one of the indexes randomly
        }

        op_message_env_voter = max_sum_index + 1;
        // Generate a random number (0 or 1)
        //int random_choice = rand() % 2;
        double u = r2();

        // Choose randomly between values of two variables
        if (u <= ALPHA) {
            currentopinion = op_message_env_voter;

        } else {
            currentopinion = op_message_neighbour_voter;
        }
    }


    // if(kilo_uid ==12){


     //   printf("The chosen opinion is %d \n ", currentopinion);

    //}


    message.data[1] = currentopinion;
    message.data[2] = kilo_uid;
    //message.data[3]= estimateR;
    //message.data[4] = estimateB;
    //message.data[5]=estimateG;
    //
    // message.data[6]= tot_e;
    message.crc = message_crc(&message);


    //reset count array to empty
    for (int i = 0; i < 5; i++) {
        op_count[i] = 0;
    }

    //reset count array to empty
    for (int i = 0; i < 5; i++) {
        op_count_vm[i] = 0;
    }
    //go to exploration state
    current_state = EXPLORATION;
    //timer =  ran_expo(1.0/avg_exploration_time); // get the time for exploration
    timer = avg_exploration_time;
    last_changed = kilo_ticks;
    set_color(RGB(0, 0, 0));
    //reset the variable that are used to find the qr for next exploration-dissem cycle
    memset(foundmodules, 0, sizeof(foundmodules[0][0]) * 18 * 38);
    tiles_of_1_option = 0;
    tiles_of_2_option = 0;
    tiles_of_3_option = 0;
    tiles_of_4_option = 0;
    tiles_of_5_option = 0;
    total_tiles_found = 0;
    avg_neighbours = 0;

    // Reset the array to empty
    for (int i = 0; i < SWARMSIZE; i++) {
        storeid[i] = 0;
    }

}


/*-----------------------------------------------------------------------------------------------*/
/* Random Walk                                                                                   */
/*-----------------------------------------------------------------------------------------------*/
void random_walk(){
    switch( current_motion_type ) {
        case TURN_LEFT:
        case TURN_RIGHT:
            if(  kilo_ticks > last_motion_ticks + turning_ticks ) {
                /* start moving forward */
                last_motion_ticks = kilo_ticks;
                set_motion(FORWARD);
            }
        break;
        case FORWARD:
            //spinup_motors();
                //set_motors(20,20);
                    if( kilo_ticks > last_motion_ticks + max_straight_ticks ) {
                        /* perform a random turn */
                        last_motion_ticks = kilo_ticks;
                        if( rand()%2 ) {
                            set_motion(TURN_LEFT);
                            current_motion_type = TURN_LEFT;
                        }
                        else {
                            set_motion(TURN_RIGHT);
                            current_motion_type = TURN_RIGHT;
                        }
                        turning_ticks = rand()%max_turning_ticks + 1;
                    }
        break;
        case STOP:
            set_motion(STOP);
        default:
            set_motion(FORWARD);
    }
}

void setup()
{
    srand(rand_hard());

    random_walk();

    //random timing for motion
    last_motion_ticks = rand() % max_straight_ticks + 1;

    //save the current ticks for comparison later on
    last_changed = kilo_ticks;
    message.type = FROMBOT; // set I am a bot
    // Quality A=1, B=2
    //////////currentopinion = (kilo_uid -1) % GROUPS +1;
    // currentopinion = INFOPTION; //CODE FUNCTIONALITY TO CHOOSE RANDOMLY OF ANY 4 INFERIOR OPTIONS
    currentopinion = rand() % (5 + 1 - 1) + 1;
    if(kilo_uid <kval){

        model = 1; //voter
    } else{

        model = 0; //majority
    }
    // set parameters fro dissemination
    message.data[0] = currentopinion;
    //Opinion A=1 , B=2, U =3
    //red
    message.data[1] = currentopinion;
    message.data[2] = kilo_uid;
    message.crc = message_crc(&message);
    //timer =  ran_expo(1.0/avg_exploration_time); //get time to be in exploration state
    timer = avg_exploration_time;
}

int isNumberNotInArray(int number, int arr[], int size) {
    for (int i = 0; i < size; i++) {
        if (arr[i] == number) {
            return 0; // Number is found in the array
        }
    }
    return 1; // Number is not found in the array
}
/*-----------------------------------------------------------------------------------------------*/
/*                              The Exploration function                                         */
/*                                                                                               */
/*-----------------------------------------------------------------------------------------------*/
void gotoexploration(){

    //  random_walk(); //start with random walk

    //set led colours
    if (currentopinion == 1){
        set_color(RGB(3, 0, 0));

    } else if (currentopinion == 2){
        set_color(RGB(0, 0, 3));

    }else if (currentopinion == 3){
        set_color(RGB(0, 3, 0));

    }else if (currentopinion == 4){
        set_color(RGB(3, 3, 0));

    }else if (currentopinion == 5){
        set_color(RGB(3, 3, 3));

    }


    //if time for exploration not over yet, do nothing else move on to dissemination state
    if ((kilo_ticks - last_changed) < timer) {//check if still within time for exploration state or not
        //check_if_against_a_wall(); //check if hitting the wall
        double u = r2();
        if(u<0.5){
            broadcast_msg = true; //then send out message to other bots

        }else{
            broadcast_msg = false; //then send out message to other bots

        }
        if (new_message == 1) {

            if (isNumberNotInArray(received_uid, storeid, (sizeof(storeid) / sizeof(storeid[0])))) {

                //not cpunted
                if(model == 0){
                    op_count[received_option - 1] += MSG_NEIGHBOUR; //for majority rule
                    //op_count_message[received_option - 1] += MSG_NEIGHBOUR; //for majority rule
                    avg_neighbours +=1;

                }else {
                    op_message_neighbour_voter = received_option; // for voter model
                }
                // Calculate size of the array
                int size;
                for (size = 0; size < SWARMSIZE; size++) {
                    if (storeid[size] == 0) {
                        break;
                    }
                }
                storeid[size++] = received_uid;



                //check if comes here
            }


            //printf("Updated array: ");

            new_message = 0;
        }


    } else{ //if not in exploration state

        if(kilo_uid ==18){
        //  printf("%d tile my op 1, %d tile my op 2, ,%d tile my op 3, ,%d tile my op 4 ,%d tile my op 5,  %d total tiles \n", tiles_of_1_option,tiles_of_2_option,tiles_of_3_option,tiles_of_4_option,tiles_of_5_option,total_tiles_found);

            printf("Array before tiles: ");
            for (int i = 0; i < 5; i++) {
               printf("%d ", op_count[i]);
            }
            printf("\n ");
            printf("tot %d  and omg %f \n", (op_count[0]+ op_count[1]+ op_count[2]+ op_count[3]+ op_count[4]),OMG*(op_count[0]+ op_count[1]+ op_count[2]+ op_count[3]+ op_count[4]) );

            printf("%d tile my op 1, %d tile my op 2, ,%d tile my op 3, ,%d tile my op 4 ,%d tile my op 5,  %d total tiles \n", tiles_of_1_option,tiles_of_2_option,tiles_of_3_option,tiles_of_4_option,tiles_of_5_option,total_tiles_found);
           // int array_size = sizeof(storeid) / sizeof(storeid[0]);


            // Find the maximum value in the array
            //for (int i = 0; i < array_size; i++) {
              //  printf("store id %d ", storeid[i]);
              //  printf("\n ");
           // }
        }

        //
        //


        float x = OMG*(op_count[0]+ op_count[1]+ op_count[2]+ op_count[3]+ op_count[4]);
        //float x = OMG;
        //float x = (OMG/4.7)*(op_count[0]+ op_count[1]+ op_count[2]+ op_count[3]+ op_count[4]);
         x = roundf(x);
        if(kilo_uid ==18) {
            printf("x is %f \n", x);
            //x = roundf(x);
            //printf("x %f:\n ", x);
        }
        // Store the names of the variables in an array of strings
        //const char *variable_names[] = {"tiles_of_1_option", "tiles_of_2_option", "tiles_of_3_option", "tiles_of_4_option", "tiles_of_5_option"};
        int values[] = {tiles_of_1_option, tiles_of_2_option, tiles_of_3_option, tiles_of_4_option, tiles_of_5_option};
        int num_variables = sizeof(values) / sizeof(values[0]);

        // Find the maximum value
        int max_value = values[0];
        for (int i = 1; i < num_variables; ++i) {
            if (values[i] > max_value) {
                max_value = values[i];
            }
        }

        // Count the number of variables with the maximum value
        int count = 0;
        int max_indexes[num_variables];
        for (int i = 0; i < num_variables; ++i) {
            if (values[i] == max_value) {
                max_indexes[count++] = i;
            }
        }

        // If there are multiple variables with the maximum value, choose one randomly
        srand(time(NULL));
        int chosen_index;
        if (count > 1) {
            chosen_index = max_indexes[rand() % count];
        } else {
            chosen_index = max_indexes[0];
        }

        if(kilo_uid ==18){

            printf("chosen index %d:\n ", chosen_index);



        }

        op_count[chosen_index] += x;
        // Print the variable with the highest value
        //if (chosen_index+1 == 1) {
         //   op_count[0]+=tiles_of_1_option + x;

      //  } else if (chosen_index+1 == 2) {
        //    op_count[1]+=tiles_of_2_option+x;

       // } else if (chosen_index+1 == 3) {

        //    op_count[2]+=tiles_of_3_option+x;

       // } else if (chosen_index+1 == 4) {

         //   op_count[3]+=tiles_of_4_option+x;
      //  } else {

          //  op_count[4]+=tiles_of_5_option+x;
        //}

        op_count_vm[0]+=tiles_of_1_option;
        op_count_vm[1]+=tiles_of_2_option;
        op_count_vm[2]+=tiles_of_3_option;
        op_count_vm[3]+=tiles_of_4_option;
        op_count_vm[4]+=tiles_of_5_option;

        estimateR = tiles_of_1_option;
        estimateB = tiles_of_2_option;
        estimateG = tiles_of_3_option;
        estimateY = tiles_of_4_option;
        estimateBL = tiles_of_5_option;
        estimateN = avg_neighbours;

        //estimateR = op_count[0];
        //estimateB = op_count[1];
        //estimateG = op_count[2];
        //estimateY = op_count[3];
        //estimateBL = op_count[4];
        //estimateN = avg_neighbours;

        tot_e = estimateR+estimateB+estimateG+estimateY+estimateBL;
        if(kilo_uid ==18){

            printf("AFTER array TILES Array:\n ");
            for (int i = 0; i < 5; i++) {
                printf("%d ", op_count[i]);
                printf("\n ");

            }

           // printf("STORE ID Array: ");
           // for (int i = 0; i < SWARMSIZE; i++) {
          //      printf("%d ", storeid[i]);
          //  }
          //  printf("\n ");

        }


        current_state = FILTER;//go to Dissemination mode
            // set_color(RGB(0, 0, 0));


        last_changed = kilo_ticks;

        //reset the variable that are used to find the qr for next exploration-dissem cycle
       memset(foundmodules, 0, sizeof(foundmodules[0][0]) * 18 * 38);
        tiles_of_1_option = 0;
        tiles_of_2_option = 0;
        tiles_of_3_option = 0;
        tiles_of_4_option = 0;
        tiles_of_5_option = 0;
        total_tiles_found = 0;
         //Reset the array to empty
        for (int i = 0; i < SWARMSIZE; i++) {
            storeid[i] = 0;
        }

        //qratio = 0;
        // set_color(RGB(0, 0, 0));

    }

}

void wall_avoidance_function(){
    wall_avoidance_state = true;
    hit_wall = false;

    if (wall_function_state == TURN_TO_AVOID_WALL){
        // set_color(RGB(3, 0, 3));
        //printf("comes to turnning \n");
        if( rand()%2 ) {
            // while ((kilo_ticks - last_motion_ticks) < max_wall_avoidance_turning_ticks) {
            /* perform a random turn */
            set_motion(TURN_LEFT);
            current_motion_type = TURN_LEFT;
            // }
        }else {
            // while ((kilo_ticks - last_motion_ticks) < max_wall_avoidance_turning_ticks) {
            /* perform a random turn */
            set_motion(TURN_RIGHT);
            current_motion_type = TURN_RIGHT;
            //  }
        }
        last_motion_wall_ticks = kilo_ticks;
        wall_function_state = STRAIGHT_TO_AVOID_WALL;
    }
    if (wall_function_state == STRAIGHT_TO_AVOID_WALL) {
        //printf("comes to straight \n");

        if ((kilo_ticks - last_motion_wall_ticks) > max_wall_avoidance_turning_ticks) {
            /* start moving forward */
            // set_color(RGB(0, 3, 0));
            last_motion_wall_ticks = kilo_ticks;
            set_motion(FORWARD);
            wall_function_state = COMPLETE_WALL_AVOIDANCE;

        }
    }
    if (wall_function_state == COMPLETE_WALL_AVOIDANCE) {
        //printf("comes to finish avoidance \n");

        if ((kilo_ticks - last_motion_wall_ticks) > max_wall_avoidance_straight_ticks) {
            last_motion_wall_ticks = kilo_ticks;
            wall_function_state = TURN_TO_AVOID_WALL;
            wall_avoidance_state = false;
            // set_color(RGB(0, 0, 0));
        }
    }
}


void message_rx( message_t *msg, distance_measurement_t *d ) {
    // check the messages

    if(msg->type == FROMBOT){ //if message from another bot


        new_message = 1;        // Set the flag on message reception.
        received_option = msg->data[1]; //get its option
        received_uid = msg->data[2]; //get its uid

        // printf("message from robot =%d, received_option = %d \n",received_uid, received_option);
    }
    if(msg->type == GRID_MSG){ //if message from Kiogrid
        // printf("message from grid, kilotick= %d \n",kilo_ticks);
        //printf("%hhu\n", msg->data[0]);
        //printf("%hhu\n",msg->data[1]);
        //printf("%hhu\n",msg->data[2]);
        //printf("%hhu cell role\n",msg->data[3]);

        received_option_kilogrid = msg->data[2];// get the opinion of the tile
        wall_flag = msg->data[3];// if wall then 42, if near wall 62 else 0

        received_grid_msg_flag = true; //set the flag that message received from Kilogrid to true

        // if(kilo_uid == 1) {
        //     set_color(RGB(3, 0, 0));
        //     printf("received_option_kilogrid=%d, wall_flag=%d, kiloticks=%d \n", received_option_kilogrid, wall_flag, kilo_ticks);
        //     set_color(RGB(3, 3, 0));
        // }


        if (current_state == EXPLORATION){ //if the bot is in exploration state
            if(received_option_kilogrid != 0){ //if the the bot is not on the wall-white border
                if (foundmodules[msg->data[0]][msg->data[1]] == 0){ //if tile not counted previously

                    foundmodules[msg->data[0]][msg->data[1]] = 1; //set the flag that tile has been counted now
                    total_tiles_found += 1;

                    if(received_option_kilogrid==1){ //if I am Red and I receive red from kilogrid
                        tiles_of_1_option += MSG_KILOG ;
                        if(kilo_uid ==1) {
                            // printf("%d tile my op 1,  %d total tiles, kilotick = %d  \n", tiles_of_1_option,
                            //        total_tiles_found, kilo_ticks);
                        }
                    }else if(received_option_kilogrid==2) { //if I am blue and I receive blue from Kilogrid
                        tiles_of_2_option += MSG_KILOG ;
                        if(kilo_uid ==1) {

                            // printf("%d tile my op 2  %d total tiles, kilotick = %d   \n", tiles_of_2_option, total_tiles_found, kilo_ticks);
                        }
                    }else if(received_option_kilogrid==3 ){ //if I am green and I receive green from Kilogrid
                        tiles_of_3_option += MSG_KILOG ;
                        if(kilo_uid ==1) {

                            // printf("%d tile my op 3,  %d total tiles, kilotick = %d  \n", tiles_of_3_option,
                            //        total_tiles_found,kilo_ticks);
                        }

                    }else if(received_option_kilogrid==4 ){ //if I am yellow and I receive yellow from Kilogrid
                        tiles_of_4_option += MSG_KILOG ;
                        if(kilo_uid ==1) {

                            // printf("%d tile my op 4 ,  %d total tiles, kilotick = %d  \n", tiles_of_4_option,
                            //        total_tiles_found,kilo_ticks);
                        }

                    }else if(received_option_kilogrid==5){ //if I am black and I receive black from Kilogrid
                        tiles_of_5_option += MSG_KILOG ;
                        if(kilo_uid ==1) {

                            // printf("%d tile my op 5,  %d total tiles, kilotick = %d  \n", tiles_of_5_option,
                            //        total_tiles_found,kilo_ticks);
                        }

                    }


                }
            }
        }

        // printf("%hhu\n",msg->data[2]);
        // printf("%hhu\n",msg->data[3]);
        if (wall_flag == 62 || wall_flag == 42){  // robot sensed wall or near wall
            //  printf("received hitwall option");
            hit_wall = true; //-> set hit wall flag to true
            if(wall_flag == 62){ //if near the border of wall and not on white wall

                kilogrid_commitment = msg->data[2]; //still get the opinion from grid
                //printf("gets commitments\n");

            }
        }else{
            hit_wall = false; //not hitting the wall
            kilogrid_commitment = msg->data[2]; //get the opinion from kilogrid
        }

    }
    if(msg->type == INIT_MSG && !init_flag){
        // example usage
//        kilogrid_commitment = msg->data[0];
//        my_commitment_quality = msg->data[1];
//        NUMBER_OF_OPTIONS = msg->data[2];
//        option_to_sample = rand() % NUMBER_OF_OPTIONS;
//        current_ground = msg->data[3];
//        communication_range = msg->data[4];

        init_flag = true;
    }else if(msg->type == GRID_MSG && init_flag){
        //received_grid_msg_flag = true;
    }else if(msg->type == VIRTUAL_AGENT_MSG  && init_flag){
        //received_virtual_agent_msg_flag = true;
    }
    return;
}

void message_tx_success(){ //if transmitted
    broadcast_msg = false; //set transmitted flag to false
    //set the colour

    // set_color(RGB(2, 0, 2));
    // delay(10);
    // set_color(RGB(0, 0, 0));


}
message_t *message_tx()
{
    if( broadcast_msg ) { //if broadcast message flag is set to true (only in dissem state function)
        return &message;
    }
    return 0;
}

int get_majority_color_opinion_sensor() {
    int values[5] = {tiles_of_1_option, tiles_of_2_option, tiles_of_3_option, tiles_of_4_option, tiles_of_5_option};
    int max_value = values[0];
    int max_indices[5];
    int max_count = 0;

    // Step 1: Find the maximum value
    for (int i = 1; i < 5; i++) {
        if (values[i] > max_value) {
            max_value = values[i];
        }
    }

    // Step 2: Collect indices of elements with the max value
    for (int i = 0; i < 5; i++) {
        if (values[i] == max_value) {
            max_indices[max_count] = i;
            max_count++;
        }
    }

    // Step 3: Randomly select one index if there is a tie
    srand(time(NULL));  // Seed the random number generator
    int random_index = max_indices[rand() % max_count];
    // printf("op1 = %d, op2 = %d, op3 = %d, op4 = %d, op5 = %d. Majority Color = %d \n",
    //     tiles_of_1_option,tiles_of_2_option,tiles_of_3_option,tiles_of_4_option,tiles_of_5_option, random_index+1);
    return random_index+1;
}
void print_sensor_opinion_count() {
    printf("Sensor Color Reading- 1:%d, 2:%d, 3:%d, 4:%d, 5:%d",tiles_of_1_option,tiles_of_2_option,
        tiles_of_3_option,tiles_of_4_option,tiles_of_5_option);
}

void clear_color_opinion_counts() {
    tiles_of_1_option=0;
    tiles_of_2_option=0;
    tiles_of_3_option=0;
    tiles_of_4_option=0;
    tiles_of_5_option=0;
}

// Function to find the index of the highest value in the array
int find_highest_index(double arr[], int size) {
    // double max_value = -3.0;
    // int max_index = -1;
    // for(int i=0; i<size; i++) {
    //     if(arr[i] > max_value) {
    //         max_value = arr[i];
    //         max_index = i;
    //     }
    // }
    // return max_index+1;
    double max_value = arr[0];
    int indices[size];
    int count = 0;

    // Find the maximum value and store all indices with this value
    for (int i = 0; i < size; i++) {
        if (arr[i] > max_value) {
            max_value = arr[i];
            count = 0;  // Reset the count
            indices[count++] = i;  // Store the index of the new maximum
        } else if (arr[i] == max_value) {
            indices[count++] = i;  // Store the index if it matches the current maximum
        }
    }

    // Randomly select one index if there are multiple with the same maximum value
    srand(time(NULL));  // Seed the random number generator
    int random_index = rand() % count;
    return indices[random_index]+1;
}

void loop()
{
    if(init_flag){  // initialization happened and messaged received from Kilogrid

        // if (received_grid_msg_flag) {
        //random_walk();
        //update_grid_msg();
        // check_if_against_a_wall();  // checks if the robot is on wall
        // received_grid_msg_flag = false;
        // }

        if (received_virtual_agent_msg_flag) {
            // update_virtual_agent_msg();
            received_virtual_agent_msg_flag = false;
        }

    }

    if ( wall_avoidance_state || hit_wall ) {
        // printf("wall avoidance \n");
        wall_avoidance_function();
    } else {
        random_walk();
    }

    if (current_state == EXPLORATION){ // if state is set to 0

        //set led colours
        if (currentopinion == 1){ // RED
            set_color(RGB(3, 0, 0));
            // delay(300);
            // set_color(RGB(0, 0, 0));
            // delay(100);
            // set_color(RGB(3, 0, 0));
        } else if (currentopinion == 2){ // BLUE
            set_color(RGB(0, 0, 3));
            // delay(300);
            // set_color(RGB(0, 0, 0));
            // delay(100);
            // set_color(RGB(0, 0, 3));

        }else if (currentopinion == 3){ // GREEN
            set_color(RGB(0, 3, 0));
            // delay(300);
            // set_color(RGB(0, 0, 0));
            // delay(100);
            // set_color(RGB(0, 3, 0));

        }else if (currentopinion == 4){ // PURPLE
            set_color(RGB(3, 0, 3));
            // delay(300);
            // set_color(RGB(0, 0, 0));
            // delay(100);
            // set_color(RGB(3, 0, 3));

        }else if (currentopinion == 5){ // YELLOW
            set_color(RGB(3, 3, 0));
            // delay(300);
            // set_color(RGB(0, 0, 0));
            // delay(100);
            // set_color(RGB(3, 3, 0));

        }else {
            set_color(RGB(0, 0, 0));
        }

        // printf("Exploration\n");
        // gotoexploration(); //go to exploration

        if(new_message == 1) {
            new_message = 0;
            if(uidSet.size == 0) opinion_receive_start_time = kilo_ticks;
            if(add_uid(&uidSet,received_uid)) {
                add_color_opinion(&colorSet,received_option);
            }
            // if(kilo_uid == 15) {
            //     printf("Received Color = %d \n",received_option);
            // }
            if(uidSet.size == NUM_OF_NEIGHBOURS) {
                int maj_col_op = get_majority_color_opinion_sensor();
                if(kilo_uid == 15 || kilo_uid == 34 || kilo_uid == 10) {
                    printf("KiloID: %d 8 unique opinions received in = %d \n",kilo_uid,(kilo_ticks - opinion_receive_start_time));
                    print_color_opinions(&colorSet);
                    print_sensor_opinion_count();
                    printf("Majority Color sensor= %d\n",maj_col_op);
                }
                for(int i=1; i<=5; i++) {
                    //TODO: Calculate like in MA for each color in a decionary with social and personal opinion and find highest of this dict to update personal opinion
                    int mi = get_color_opinion_count(&colorSet, i);
                    int m = NUM_OF_NEIGHBOURS;
                    double personal_info_weight = 0.75;
                    double value_for_dict = mi + (personal_info_weight * m * ( i == maj_col_op ? 1: 0));
                    if(kilo_uid == 15|| kilo_uid == 34 || kilo_uid == 10) {
                        printf("i=%d, mi = %d, maj_col_op= %d, value_for_dict=%f \n",i,mi,maj_col_op,value_for_dict);
                    }
                    decision_arr[i-1] = value_for_dict;
                }
                if(INFORMED) {
                    currentopinion = find_highest_index(decision_arr, MAX_COLOR_OPINIONS);
                }
                if(kilo_uid == 15|| kilo_uid == 34 || kilo_uid == 10) {
                    printf("KiloID= %d Decision Arr: ", kilo_uid);
                    for(int i=0;i<5;i++) {
                        printf("%f, ",decision_arr[i]);
                    }
                    printf("curr_opinion = %d \n",currentopinion);
                    printf("-----------------\n");
                }

                clear_uid_hashset(&uidSet);
                clear_color_hashset(&colorSet);
                clear_color_opinion_counts();
            }
        }

        if(kilo_ticks % 100 == 0) {
            message.data[1] = currentopinion;
            message.data[2] = kilo_uid;
            message.crc = message_crc(&message);
            broadcast_msg = true;
        }
    }



    // if (current_state == FILTER){  // state is set to choose between Vote or Noise
    //
    //     printf("Filter");
    //
    //     //get the random number 0-1 to flip between self-sourced or social
    //     // double u = r2();
    //     poll();
    // }
    // debug info - is now also important for the inter-robot communication, so do not delete
    debug_info_set(currentopinion, currentopinion);
    debug_info_set(estimateR, estimateR);
    debug_info_set(estimateB, estimateB);
    debug_info_set(estimateG, estimateG);
    debug_info_set(estimateY, estimateY);

    debug_info_set(estimateBL, estimateBL);
    debug_info_set(estimateN, estimateN);


    debug_info_set(tot_e, tot_e);
    debug_info_set(kilo_uid, kilo_uid);
}

int main()
{
    // initialize the hardware of the robot
    kilo_init();
    // create debug struct - mimics the communication with the kilogrid
    debug_info_create();
    // callback for received messages
    kilo_message_rx = message_rx;
    // start control loop

    // Register the message_tx callback function.
    kilo_message_tx = message_tx;
    // Register the message_tx_success callback function.
    kilo_message_tx_success = message_tx_success;
    kilo_start(setup, loop);
    return 0;
}

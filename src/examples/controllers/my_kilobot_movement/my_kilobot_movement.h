//
// Created by nomaan on 8/9/24.
//

#ifndef MY_KILOBOT_MOVEMENT_H
#define MY_KILOBOT_MOVEMENT_H

/*
 * Include some necessary headers.
 */

/* Definition of the CCI_Controller class. */
#include <argos3/core/control_interface/ci_controller.h>
/* Definition of the differential steering actuator */
#include <argos3/plugins/robots/generic/control_interface/ci_differential_steering_actuator.h>
/* Random number generator */
#include <argos3/core/utility/math/rng.h>
#include <argos3/core/utility/logging/argos_log.h>

#include "plugins/robots/kilobot/control_interface/kilolib.h"
#include "plugins/robots/kilobot/control_interface/message.h"
/* Definition of the kilobot light sensor */
#include <argos3/plugins/robots/kilobot/control_interface/ci_kilobot_light_sensor.h>

#include "plugins/robots/kilobot/control_interface/ci_kilobot_communication_actuator.h"
#include "plugins/robots/kilobot/control_interface/ci_kilobot_communication_sensor.h"
#include "plugins/robots/kilobot/control_interface/ci_kilobot_led_actuator.h"
/*
 * All the ARGoS stuff in the 'argos' namespace.
 * With this statement, you save typing argos:: every time.
 */
using namespace argos;


enum TStateNames {KILOBOT_STATE_STOP, KILOBOT_STATE_TURNING, KILOBOT_STATE_MOVING};

/*
 * A controller is simply an implementation of the CCI_Controller class.
 */
class CKilobotMovement : public CCI_Controller {

public:

   /* Class constructor. */
   CKilobotMovement();

   /* Class destructor. */
   virtual ~CKilobotMovement() {}

   /*
    * This function initializes the controller.
    * The 't_node' variable points to the <parameters> section in the XML
    * file in the <controllers><kilobot_diffusion_controller> section.
    */
   virtual void Init(TConfigurationNode& t_node);


   /*
    * This function is called once every time step.
    * The length of the time step is set in the XML file.
    */
   virtual void ControlStep();
   // virtual void MessageRX(message_t *message, distance_measurement_t *distance_measurement);
   // virtual message_t *MessageTx();
   // virtual void MessageTxSuccess();
   virtual void StoreMessage(message_t pt_message);
   virtual void HandleReceivedMessage(const message_t& t_message);
   /*
    * This function resets the controller to its state right after the
    * Init().
    * It is called when you press the reset button in the GUI.
    * In this example controller there is no need for resetting anything,
    * so the function could have been omitted. It's here just for
    * completeness.
    */
   virtual void Reset();

   /*
    * Called to cleanup what done by Init() when the experiment finishes.
    * In this example controller there is no need for clean anything up,
    * so the function could have been omitted. It's here just for
    * completeness.
    */
   virtual void Destroy() {}

   /*
    * These functions allow to track the current state of the robot
    */
   inline const TStateNames GetCurrentState() const {return m_tCurrentState;};
   inline const bool StateChanged() const {return (m_tPreviousState != m_tCurrentState);};

private:

   /*
    * The following variables are used as parameters for the
    * algorithm. You can set their value in the <parameters> section
    * of the XML configuration file, under the
    * <controllers><kilobot_diffusion_controller> section.
    */

   /* Pointer to the differential steering actuator */
   CCI_DifferentialSteeringActuator* m_pcMotors;
   CCI_KilobotCommunicationSensor* m_pcCommunicationSensor;
   CCI_KilobotCommunicationActuator* m_pcCommunicationActuator;
   CCI_KilobotLEDActuator* m_pcLEDActuator;

   /* behavioural state (moving/turning) */
   TStateNames m_tCurrentState;
   TStateNames m_tPreviousState;

   /* counters for random walk behaviour */
   UInt32 m_unMaxMotionSteps;
   UInt32 m_unCountMotionSteps;

   UInt32 m_unMaxTurningSteps;
   UInt32 m_unCountTurningSteps;
   UInt32 m_timestepCounter;
   int newMessage;
   int distance;
   // UInt16 senderId;
   // UInt8 receivedColor;
   // int receivedMessageData;
 // Message structure
   message_t m_tMessage;
   int messageSent;

   // /* Pointer to the loght sensor actuator */
   // CCI_KilobotLightSensor* m_pcLightSensor;

   struct Message {
    int receivedMessageData; // Custom type to identify the message
    int senderId;
    int receivedColor; // The integer value you want to send
   };


   /* actual motor speed */
   Real   m_fMotorL;
   Real   m_fMotorR;

   /* variables for the random number generation */
   CRandom::CRNG*  m_pcRNG;
};

#endif

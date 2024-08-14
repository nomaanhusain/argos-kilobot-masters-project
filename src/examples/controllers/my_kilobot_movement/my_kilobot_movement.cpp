//
// Created by nomaan on 8/9/24.
//

/* Include the controller definition */
#include "my_kilobot_movement.h"
/* Function definitions for XML parsing */
#include <argos3/core/utility/configuration/argos_configuration.h>
/* 2D vector definition */
#include <argos3/core/utility/math/vector2.h>
#include <vector>
#include <algorithm>
#include <argos3/core/utility/datatypes/color.h>

#include "plugins/robots/kilobot/control_interface/kilolib.h"


#define PIN_FORWARD 1.0f;
#define PIN_TURN    1.57f;
#define PIN_STOP    0.0f;

CKilobotMovement::CKilobotMovement():
    m_pcMotors(NULL),
    m_pcCommunicationSensor(NULL),
    m_pcCommunicationActuator(NULL),
    m_pcLEDActuator(NULL),
    // m_pcLightSensor(NULL),
    m_tCurrentState(KILOBOT_STATE_STOP),
    m_tPreviousState(KILOBOT_STATE_STOP),
    m_unMaxMotionSteps(50),
    m_unCountMotionSteps(0),
    m_unMaxTurningSteps(50), // = pi/(omega delta_t) = pi/(v*delta_t/l) = (pi*l)/(v*delta_t)
    m_unCountTurningSteps(100),
    newMessage(1),
    distance(0),
    // senderId(-1),
    // receivedColor(0),
    // receivedMessageData(-1),
    m_tMessage(),
    messageSent(0),
    m_timestepCounter(0),
    m_fMotorL(0.0f),
    m_fMotorR(0.0f)
    {
        m_pcRNG = CRandom::CreateRNG( "argos" );
    }

void CKilobotMovement::Init(TConfigurationNode& t_node) {
   /*
    * Get sensor/actuator handles
    *
    * The passed string (ex. "differential_steering") corresponds to the
    * XML tag of the device whose handle we want to have. For a list of
    * allowed values, type at the command prompt:
    *
    * $ argos3 -q actuators
    *
    * to have a list of all the possible actuators, or
    *
    * $ argos3 -q sensors
    *
    * to have a list of all the possible sensors.
    *
    * NOTE: ARGoS creates and initializes actuators and sensors
    * internally, on the basis of the lists provided the configuration
    * file at the <controllers><kilobot_diffusion><actuators> and
    * <controllers><kilobot_diffusion><sensors> sections. If you forgot to
    * list a device in the XML and then you request it here, an error
    * occurs.
    */
   // Get sensor/actuator handles
   m_pcMotors    = GetActuator<CCI_DifferentialSteeringActuator>("differential_steering");
   m_pcCommunicationSensor = GetSensor<CCI_KilobotCommunicationSensor>("kilobot_communication");
   m_pcCommunicationActuator = GetActuator<CCI_KilobotCommunicationActuator>("kilobot_communication");
   m_pcLEDActuator = GetActuator<CCI_KilobotLEDActuator>("kilobot_led");

   // m_pcLightSensor = GetSensor<CCI_KilobotLightSensor>("kilobot_light");

   // Parse the configuration file
   GetNodeAttributeOrDefault(t_node, "max_motion_steps", m_unMaxMotionSteps, m_unMaxMotionSteps );
   if( m_unMaxMotionSteps == 0 ) {
      LOGERR << "[FATAL] Invalid value for num_moving_steps (" << m_unMaxMotionSteps << "). Should be a positive integer." << std::endl;
   }

   Reset();
}



/****************************************/
/****************************************/

void CKilobotMovement::Reset() {
   // reset/intialise the robot state
   m_unCountMotionSteps = m_pcRNG->Uniform(CRange<UInt32>(1,m_unMaxMotionSteps+1));
   m_tCurrentState = KILOBOT_STATE_MOVING;
   m_tPreviousState = KILOBOT_STATE_MOVING;
   m_fMotorL = m_fMotorR = PIN_FORWARD;
}

/****************************************/
/****************************************/
// void CKilobotMovement::MessageRX(message_t *message, distance_measurement_t *distance_measurement) {
//    std::cout << "Controller: Message Received " << "\n";
//    // Set flag on message reception.
//    newMessage = 1;
//
//    distance = estimate_distance(distance_measurement);
//    receivedMessageData = message->data[0];
//    senderId = message->data[1];
//    // receivedColor = message->data[2];
// }
//
void CKilobotMovement::StoreMessage(message_t pt_message) {
   // Store the message pointer to be sent in the next transmission cycle
   m_tMessage = pt_message;
}
//
//
// message_t *CKilobotMovement::MessageTx() {
//    std::cout << "Controller: MessageTx called" << "\n";
//    return message;
// }
//
// void CKilobotMovement::MessageTxSuccess() {
//    messageSent = 1;
// }

void CKilobotMovement::HandleReceivedMessage(const message_t& t_message) {

   int received_value = t_message.data[0];
   int sender_id = t_message.data[1]; // Assuming you stored your int value at data[1]
   int received_color = t_message.data[2];

   std::cout << "CONTOLLER-RD: val= " << received_value << "sender_id= " << sender_id << "rec_col= " << received_color
         << "\n";
   if(received_value > 0) {
      // Set LED to green
      m_pcLEDActuator->SetColor(CColor::GREEN);
   } else {
      // Set LED to red
      m_pcLEDActuator->SetColor(CColor::RED);
   }
}

void CKilobotMovement::ControlStep() {

   ++m_timestepCounter;

   // Send the message
   if (m_timestepCounter % 30 == 0) {
      std::cout << "CONTOLLER: Sending message. id= "<< GetId() <<"Timestep= "<< m_timestepCounter << "\n";
      m_pcCommunicationActuator->SetMessage(&m_tMessage);
   }
   // // Handle received messages
   // std::cout << "CONTOLLER: Receiving message" << "\n";
   const CCI_KilobotCommunicationSensor::TPackets& packets = m_pcCommunicationSensor->GetPackets();
   for(const auto& packet : packets) {

      // std::cout << "CONTOLLER-RD: val= " << packet.Message->data[0] << "sender_id= " << packet.Message->data[1] << "rec_col= " << packet.Message->data[2]<<"\n";
      // std::cout << "CONTOLLER-RD: val= " << packet.Message->data[0] <<"\n";
      // HandleReceivedMessage(*packet.Message);

      // Check if the message pointer is not null
      if(packet.Message != nullptr) {
         // Safely access the message data
         // std::cout << "CONTROLLER-RD: val= " << static_cast<int>(packet.Message->data[0]) << "\n";
         // std::cout << "CONTOLLER-RD: val= " << static_cast<int>(packet.Message->data[0]) << "sender_id= " <<
         //    static_cast<int>(packet.Message->data[1]) << "rec_col= " << static_cast<int>(packet.Message->data[2])<<"\n";
         std::cout << "CONTOLLER-RD: val= " << packet.Message->data[0] << "sender_id= " << packet.Message->data[1] << "rec_col= " << packet.Message->data[2]<<"\n";
         // Example: Change LED color based on the received value
         if(packet.Message->data[0] > 0) {
            m_pcLEDActuator->SetColor(CColor::GREEN);
         }
      } else {
         std::cout << "CONTROLLER-RD: No message received or message is null.\n";
      }
   }





   // compute the robot motion: move forward for a fixed amount of
   // time, and rotate cw/ccw for a random amount of time
   // max rotation: 180 degrees as determined by m_unMaxTurningSteps
   m_tPreviousState = m_tCurrentState;
   // std::cout << "  From Conroller: " << m_tPreviousState << "\n";
   switch(m_tCurrentState) {
   case KILOBOT_STATE_TURNING:
      if( --m_unCountTurningSteps == 0 ) {
         m_fMotorL = m_fMotorR = PIN_FORWARD;
         m_unCountMotionSteps = m_unMaxMotionSteps;
         m_tCurrentState = KILOBOT_STATE_MOVING;
      }
      break;

   case KILOBOT_STATE_MOVING:
      if( --m_unCountMotionSteps == 0 ) {
         UInt32 direction = m_pcRNG->Uniform(CRange<UInt32>(0,2));
         if( direction == 0 ) {
            m_fMotorL = PIN_TURN;
            m_fMotorR = PIN_STOP;
         }
         else {
            m_fMotorL = PIN_STOP;
            m_fMotorR = PIN_TURN;
         }
         m_unCountTurningSteps = m_pcRNG->Uniform(CRange<UInt32>(1,m_unMaxTurningSteps));
         m_tCurrentState = KILOBOT_STATE_TURNING;
      }
      break;

   case KILOBOT_STATE_STOP:
   default:
      m_fMotorL = m_fMotorR = PIN_STOP;
      break;
   };

   m_pcMotors->SetLinearVelocity(m_fMotorL, m_fMotorR);
}


REGISTER_CONTROLLER(CKilobotMovement, "my_kilobot_movement")


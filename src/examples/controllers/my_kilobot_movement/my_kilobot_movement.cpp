//
// Created by nomaan on 8/9/24.
//

/* Include the controller definition */
#include "my_kilobot_movement.h"
/* Function definitions for XML parsing */
#include <argos3/core/utility/configuration/argos_configuration.h>
/* 2D vector definition */
#include <argos3/core/utility/math/vector2.h>
#include <utility>
#include <vector>
#include <algorithm>
#include <argos3/core/utility/datatypes/color.h>
#include <bits/random.h>

#include "plugins/robots/kilobot/control_interface/kilolib.h"


#define PIN_FORWARD 1.0f;
#define PIN_TURN    1.57f;
#define PIN_STOP    0.0f;

CKilobotMovement::CKilobotMovement():
    m_pcMotors(NULL),
    m_pcCommunicationSensor(NULL),
    m_pcCommunicationActuator(NULL),
    m_pcLEDActuator(NULL),
    m_tCurrentState(KILOBOT_STATE_STOP),
    m_tPreviousState(KILOBOT_STATE_STOP),
    m_unMaxMotionSteps(50),
    m_unCountMotionSteps(0),
    m_unMaxTurningSteps(50), // = pi/(omega delta_t) = pi/(v*delta_t/l) = (pi*l)/(v*delta_t)
    m_unCountTurningSteps(100),
    m_tMessage(),
    m_firstMessageTimestep(0),
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

   // Generate the filename based on this robot's ID
   std::string filename = "time_output/robot_" + GetId() + "_times.txt";
   m_cOutputFile.open(filename, std::ios_base::trunc | std::ios_base::out);

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

void CKilobotMovement::StoreMessage(message_t pt_message) {
   // Store the message pointer to be sent in the next transmission cycle
   m_tMessage = pt_message;
}
void CKilobotMovement::StoreColorCounts(std::map<std::string, int> color_counts) {
   currColorCounts = std::move(color_counts);
}

void CKilobotMovement::HandleReceivedMessage(const message_t& t_message) {

   int sender_id = t_message.data[0];
   int color_name = t_message.data[1]; // Assuming you stored your int value at data[1]
   int received_color = t_message.data[2];
   Real probability = 0.2f;
   // Generate a random number between 0 and 1
   Real random_number = m_pcRNG->Uniform(CRange<Real>(0.0f, 1.0f));
   if (random_number < probability) {
      color_name = 0; // Set to 0 with the specified probability
   }
   if(uniqueRobotIds.empty()) m_firstMessageTimestep = m_timestepCounter;
   uniqueRobotIds.insert(sender_id);
   if(uniqueRobotIds.size() == 8) {
      UInt32 timeTaken = m_timestepCounter-m_firstMessageTimestep;
      // std::cout << "Received messages from 8 unique robots, time req= " << timeTaken << std::endl;
      //Write time to file
      m_cOutputFile << timeTaken << std::endl;

      // Clear the set to start counting again for the next set of unique robots
      uniqueRobotIds.clear();
   }

   std::cout << "CONTOLLER-RD: sender_id= " << sender_id << "color_name= " << color_name << "rec_col= " << received_color << "\n";
   if(received_color > 0) {
      // Set LED to green
      m_pcLEDActuator->SetColor(CColor::GREEN);
   } else {
      // Set LED to red
      m_pcLEDActuator->SetColor(CColor::RED);
   }
}

void CKilobotMovement::ControlStep() {

   // for (const auto& colorEntry : currColorCounts) {
   //     std::cout << "  Color: " << colorEntry.first << ", Count: " << colorEntry.second << "\n";
   // }

   ++m_timestepCounter;

   // Send the message, the timing is slightly radomized
   if (m_timestepCounter % (30 + (std::rand()%(20-5+1))) == 0) {
      // std::cout << "CONTOLLER: Sending message. id= "<< GetId() <<"Timestep= "<< m_timestepCounter << "\n";
      m_pcCommunicationActuator->SetMessage(&m_tMessage);
   }

   // // Handle received messages
   const CCI_KilobotCommunicationSensor::TPackets& packets = m_pcCommunicationSensor->GetPackets();
   for(const auto& packet : packets) {

      // Check if the message pointer is not null
      if(packet.Message != nullptr) {
         // Safely access the message data
         HandleReceivedMessage(*packet.Message);
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


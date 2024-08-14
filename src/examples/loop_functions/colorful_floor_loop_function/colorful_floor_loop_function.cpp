#include "colorful_floor_loop_function.h"

#include <random>
#include <argos3/core/simulator/entity/floor_entity.h>
#include <argos3/core/utility/math/rng.h>
#include <argos3/plugins/simulator/entities/box_entity.h>
#include <argos3/plugins/robots/kilobot/simulator/kilobot_entity.h>

#include "examples/controllers/my_kilobot_movement/my_kilobot_movement.h"
#include "plugins/robots/kilobot/control_interface/message.h"
#include "plugins/robots/kilobot/control_interface/message_crc.h"

CColorfulFloorLoopFunction::CColorfulFloorLoopFunction() :
    m_pcRNG(NULL),
    majority_color_index(0),
    m_floor(NULL){}



void CColorfulFloorLoopFunction::Init(TConfigurationNode& t_tree) {
    CLoopFunctions::Init(t_tree);

    // Get the floor entity
    m_floor = &GetSpace().GetFloorEntity();
    m_pcRNG = CRandom::CreateRNG("argos");
    // Get the arena limits
    const CVector3& cArenaMin = CSimulator::GetInstance().GetSpace().GetArenaLimits().GetMin();
    const CVector3& cArenaMax = CSimulator::GetInstance().GetSpace().GetArenaLimits().GetMax();

    // Store the min and max coordinates
    m_fMinX = cArenaMin.GetX();
    m_fMaxX = cArenaMax.GetX();
    m_fMinY = cArenaMin.GetY();
    m_fMaxY = cArenaMax.GetY();
    std::vector<CColor> vecColors = {CColor::RED, CColor::BLUE, CColor::YELLOW, CColor::GREEN};
    UpdateFloorColors(vecColors, majority_color_index);
    majority_color_index = (majority_color_index + 1) % sizeof(vecColors);
    m_cOutput.open("ColorCounts.txt", std::ios_base::trunc | std::ios_base::out);
    // UpdateFloorColors();
}

void CColorfulFloorLoopFunction::Reset() {
    // Reset the floor colors if necessary
    //m_mapColorSeenCounts.clear();
    m_cOutput << "ENDDD RESET" << std::endl;
}
void CColorfulFloorLoopFunction::Destroy() {
    m_cOutput << "robID\tcolor\tcount" << std::endl;
    for (const auto& robotEntry : robotColorCounts) {
        int robotId = robotEntry.first;
        const auto& colorCounts = robotEntry.second;
        //Write stuff to the file
        for (const auto& colorEntry : colorCounts) {
            m_cOutput << robotId << "\t" << colorEntry.first << "\t" << colorEntry.second << "\n" << std::endl;
        }
    }
}

CColor CColorfulFloorLoopFunction::GetFloorColor(const CVector2& floor_plane) {
    // Convert floor coordinates to indices
    int x = static_cast<int>(floor_plane.GetX() * 20); // Adjust scaling factor as needed
    int y = static_cast<int>(floor_plane.GetY() * 20); // Adjust scaling factor as needed


    // Return the stored color for this tile
    return m_mapFloorColors[std::make_pair(x, y)];
}
void CColorfulFloorLoopFunction::PreStep() {
    UInt32 time = GetSpace().GetSimulationClock();
    std::vector<CColor> vecColors = {CColor::RED, CColor::BLUE, CColor::YELLOW, CColor::GREEN};
    // Change floor color at a defined timestep
    if (time%50 == 0) {
        UpdateFloorColors(vecColors, majority_color_index);
        majority_color_index = majority_color_index + 1;
        if( majority_color_index == vecColors.size()) majority_color_index = 0;
        m_floor->SetChanged();
    }
}

void CColorfulFloorLoopFunction::PostStep() {
    UpdateColorSeenCounts();
}

void CColorfulFloorLoopFunction::UpdateColorSeenCounts() {
    // Iterate through all robots in the arena
    CSpace::TMapPerType& tFBMap = GetSpace().GetEntitiesByType("kilobot");
    for (CSpace::TMapPerType::iterator it = tFBMap.begin(); it != tFBMap.end(); ++it) {
        CKilobotEntity* pcKB = any_cast<CKilobotEntity*>(it->second);
        // CKilobotEntity& pcKB = *any_cast<CKilobotEntity*>(it->second);
        std::string strRobotID = pcKB->GetId();
        CVector2 cFBPos = CVector2(pcKB->GetEmbodiedEntity().GetOriginAnchor().Position.GetX(),
                                       pcKB->GetEmbodiedEntity().GetOriginAnchor().Position.GetY());

        CColor fl_color  = GetFloorColor(cFBPos);
        // CColor fl_color = CColor::RED;
        std::string color_name = std::to_string(fl_color);
        int rob_id = std::stoi(strRobotID);
        //
        // // Increment the count of the color seen by the robot
        robotColorCounts[rob_id][color_name]++;

        // Get the Kilobot controller

        CKilobotMovement& cController = dynamic_cast<CKilobotMovement&>(pcKB->GetControllableEntity().GetController());
        // // Prepare a message
        message_t tMessage;
        tMessage.type = NORMAL;
        tMessage.data[0] = 1;
        tMessage.data[1] = rob_id; // Upper 8 bits of ID
        tMessage.data[2] = 43;  // Set to 1 if red, else 0
        // tMessage.crc = message_crc(&tMessage);

        // Store the message in the Kilobot
        // std::cout << "Rob_id: "<< rob_id << " LOOP FUNC: Calling StoreMessage()"<<"\n";
        cController.StoreMessage(tMessage);
        // // Send the message
        // std::cout << "Rob_id: "<< rob_id << " LOOP FUNC: Calling MessageTx()"<<"\n";
        // cController.MessageTx();

        // argos::LOG << "ID = " << int_id << "Color = " << fl_color << std::endl;
        // Display the results
        // for (const auto& robotEntry : robotColorCounts) {
        //     int robotId = robotEntry.first;
        //     const auto& colorCounts = robotEntry.second;
        //     std::cout << "Robot ID: " << robotId << "\n";
        //     for (const auto& colorEntry : colorCounts) {
        //         std::cout << "  Color: " << colorEntry.first << ", Count: " << colorEntry.second << "\n";
        //     }
        // }
    }
    //argos::LOG << "Seen Count" << m_mapColorSeenCounts << std::endl;
}

void CColorfulFloorLoopFunction::UpdateFloorColors(const std::vector<CColor>& vecColors, UInt32 majority_color_index) {
    m_mapFloorColors.clear();

    // Calculate the number of tiles
    int num_tiles_x = static_cast<int>((m_fMaxX - m_fMinX) * 20) + 1;
    int num_tiles_y = static_cast<int>((m_fMaxY - m_fMinY) * 20) + 1;
    int total_tiles = num_tiles_x * num_tiles_y;

    // Determine the number of tiles for the majority color (70%)
    int num_majority_tiles = static_cast<int>(0.7 * total_tiles);

    // Create a vector of tile colors
    std::vector<CColor> vecTileColors(total_tiles);

    // Assign the majority color to the first 70% of the vector
    std::fill(vecTileColors.begin(), vecTileColors.begin() + num_majority_tiles, vecColors[majority_color_index]);

    // Assign random colors from the array to the remaining 30% of the vector
    int num_remaining_colors = vecColors.size();
    for (int i = num_majority_tiles; i < total_tiles; ++i) {
        UInt32 color_index;
        do {
            color_index = m_pcRNG->Uniform(CRange<UInt32>(0, num_remaining_colors));
        } while (color_index == majority_color_index); // Ensure not to pick the majority color again
        vecTileColors[i] = vecColors[color_index];
    }

    // Shuffle the vector to distribute colors randomly
    std::shuffle(vecTileColors.begin(), vecTileColors.end(), std::default_random_engine(m_pcRNG->Uniform(CRange<UInt32>(0, 10000))));

    // Assign colors to the floor tiles based on the shuffled vector
    int index = 0;
    for (int x = static_cast<int>(m_fMinX * 20); x <= static_cast<int>(m_fMaxX * 20); ++x) {
        for (int y = static_cast<int>(m_fMinY * 20); y <= static_cast<int>(m_fMaxY * 20); ++y) {
            m_mapFloorColors[std::make_pair(x, y)] = vecTileColors[index++];
        }
    }
}

REGISTER_LOOP_FUNCTIONS(CColorfulFloorLoopFunction, "colorful_floor_loop_function")

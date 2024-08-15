//
// Created by nomaan on 7/4/24.
//

#ifndef COLORFUL_FLOOR_LOOP_FUNCTION_H
#define COLORFUL_FLOOR_LOOP_FUNCTION_H
#include <argos3/core/simulator/loop_functions.h>
#include <argos3/core/simulator/entity/floor_entity.h>
#include <argos3/core/utility/math/range.h>
#include <argos3/core/utility/math/rng.h>
#include <argos3/plugins/simulator/entities/box_entity.h>
#include <argos3/plugins/robots/kilobot/simulator/kilobot_entity.h>
using namespace argos;

class CColorfulFloorLoopFunction : public CLoopFunctions {
public:
    CColorfulFloorLoopFunction();
    virtual ~CColorfulFloorLoopFunction() {}
    virtual void Init(TConfigurationNode& t_tree);
    virtual void Reset();
    virtual void Destroy();
    virtual void PostStep();
    virtual void PreStep();
    virtual CColor GetFloorColor(const CVector2& robot_coordinate);
    virtual void UpdateFloorColors(const std::vector<CColor>& vecColors, UInt32 majority_color_index);
    virtual void UpdateColorSeenCounts();

private:
    // Real m_fTileSize;
    // std::vector<CBoxEntity*> m_vecTiles;
    // CColor m_cColors[4];
    CFloorEntity* m_floor;
    CRandom::CRNG* m_pcRNG;
    std::map<std::pair<int, int>, CColor> m_mapFloorColors; // Map to store the colors of the floor tiles
    Real m_fMinX, m_fMaxX, m_fMinY, m_fMaxY;
    int majority_color_index;
    std::map<int, std::map<std::string, int>> robotColorCounts;
    std::ofstream m_cOutput;

};
#endif //COLORFUL_FLOOR_LOOP_FUNCTION_H


#include "json.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <set>

using nlohmann::json;

json get_semantics(const json::iterator &it, int i = -1, int j = -1, int k = -1);
int  get_material(const json::iterator &it, int i = -1, int j = -1, int k = -1);


//------------------------------


json get_semantics(const json::iterator &it, int i, int j, int k) {
  try {
    if (it.value().is_array() == false)
      return it.value();
    else if ( (i != -1) && (it.value()[i].is_array() == false) )
      return it.value()[i];
    else if ( (j != -1) && (it.value()[i][j].is_array() == false) )
      return it.value()[i][j];
    else
      return it.value()[i][j][k];
  }
  catch (json::type_error& e) {
    json empty;
    return empty;
  }
}

int get_material(const json::iterator &it, int i, int j, int k) {
  try {
    if (it.value().is_array() == false)
      return it.value();
    else if ( (i != -1) && (it.value()[i].is_array() == false) )
      return it.value()[i];
    else if ( (j != -1) && (it.value()[i][j].is_array() == false) )
      return it.value()[i][j];
    else
      return it.value()[i][j][k];
  }
  catch (json::type_error& e) {
    return -1;
  }
}


int main(int argc, char *argv[]) {
    
    json myjson = R"(
    {
        "type": "Solid",
        "lod": 2.1,
        "boundaries": [
          [ [[0, 3, 2, 1]], [[4, 5, 6, 7]], [[0, 1, 5, 4]], [[1, 2, 6, 5]], [[2, 3, 7, 6]], [[3, 0, 4, 7]] ]
        ],
        "semantics": [
            [
             {
             "type": "RoofSurface",
             "slope": 33.4
             },
             {
             "type": "RoofSurface",
             "slope": 66.4
             },
             {},
             {},
             {
             "type": "WallSurface",
             "paint": "blue"
             },
             {
             "type": "WallSurface",
             "paint": "red"
             }
             ]
        ],
        "semantics2":
          {
           "type": "RoofSurface"
          },
        "texture": [
          [ [[0, 10, 23, 23, 11]], null, null, [[0, 13, 52, 66, 57]], [null], null ]
        ],
        "material1": [2]
    }
    )"_json;
    
  
  auto its = myjson.find("semantics");
  auto itm = myjson.find("material1");
  auto itt = myjson.find("texture");

  if (myjson["type"] == "Solid") {
    int shellid = 0;
    for (auto& shell : myjson["boundaries"]) {
      int surfaceid = 0;
      for (auto& surface : shell) {
        std::cout << surface << " --- ";
        std::cout << get_semantics(its, shellid, surfaceid) << " --- ";
        std::cout << get_material(itm, shellid, surfaceid) << std::endl;
        int ringid = 0;
        for (auto& ring : surface) {
          // std::cout << ring << std::endl;
          int vid = 0;
          std::cout << "texture: [";
          for (auto& v : ring) {
            std::cout << itt.value()[shellid][surfaceid][ringid][vid+1] << ",";
            vid++;
          }
          std::cout << "]" << std::endl;
          ringid++;
        }
        surfaceid++;
      }
      shellid++;
    }
  }
    
  return 0;
}

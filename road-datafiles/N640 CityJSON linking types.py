import gdal
import shapely
import fiona
import json

extension_url = "https://github.com/fhb1990" \
                "/cityjson/blob/master/schema/v09/extensions/roadnetwork.json"
def lod1linking():
    # Load point shapefile
    punten = fiona.open("../GIS/NodesAgain2_LoD0.1.shp")

    # Initialize CityJSON file
    cj = {}
    cj["type"] = "CityJSON"
    cj["version"] = "1.0"
    cj["extensions"] = {"RoadExt" : {"url": extension_url, "version": 1.0}}
    cj["CityObjects"] = {}
    cj["vertices"] = []

    counter = 0
    for feature in punten:
        coords = feature['geometry']['coordinates']
        new_coords = [coords[0], coords[1], 0]
        if counter == 0:
            cj["vertices"].append(new_coords)
            counter += 1
            cityobject = {"type": "+RoadNode",
                          "geometry": [],
                          "attributes": {
                              "edges": [],
                              "roadNodeType": feature["properties"]["RoadNodeTy"]
                              #"IntersectionID"
                              }
                          }
            geom = {"type": "MultiPoint",
                    "lod": 0.1,
                    "boundaries": [len(cj["vertices"]) -1]}
            
            cityobject["geometry"].append(geom)
            
            cityobject["attributes"]["edges"].append("edge" +
                str(feature["properties"]["fid"]))
            
            cj["CityObjects"]["node" + feature["id"]] = cityobject
            
        else:
            if all( abs(coords[0] - cj["vertices"][i][0]) > 0.01
                    or abs(coords[1] - cj["vertices"][i][1]) > 0.01
                    for i in range(len(cj["vertices"]))):
                cj["vertices"].append(new_coords)
                cityobject = {"type": "+RoadNode",
                              "geometry": [],
                              "attributes": {
                                  "edges": [],
                                  "roadNodeType": feature["properties"]["RoadNodeTy"]
                                  #"IntersectionID"
                                  }
                              }
                geom = {"type": "MultiPoint",
                        "lod": 0.1,
                        "boundaries": [len(cj["vertices"]) -1]}
                
                cityobject["geometry"].append(geom)
                
                cityobject["attributes"]["edges"].append(
                    "edge" + str(feature["properties"]["fid"]))
                
                cj["CityObjects"]["node" + feature["id"]] = cityobject
                
            else:
                for i in range(len(cj["vertices"])):
                    if abs(coords[0] - cj["vertices"][i][0]) < 0.01 and abs(coords[1] - cj["vertices"][i][1]) < 0.01:
                        for key in cj["CityObjects"]:
                            if i in cj["CityObjects"][key]["geometry"][0]["boundaries"]:
                                cj["CityObjects"][key]["attributes"]["edges"].append("edge" + str(feature["properties"]["fid"]))

    # Load line shapefile
    lines = fiona.open('../GIS/LoD0.1.shp')

    # Extract geometries
    for feature in lines:
        linestring = []
        cityobject = {"type": "+RoadEdge",
                      "geometry": [],
                      "attributes": {
                          "startNode": "",
                          "endNode": ""}}
        geom = {"type": "MultiLineString",
                "lod": 0.1,
                "boundaries": []}
        for coords in feature['geometry']['coordinates']:
            cj["vertices"].append([coords[0], coords[1], coords[2]])
            linestring.append(len(cj["vertices"]) -1)
        geom["boundaries"] = [linestring]
        cityobject["geometry"].append(geom)
        for key in cj["CityObjects"]:
            if key.startswith("node"):
                if "edge" + feature["id"] in cj["CityObjects"][key]["attributes"]["edges"]:
                    #node_id = int(key.replace("node",""))
                    #print( node_id, punten[node_id]["properties"]["c_Meters"])
                    #if abs(punten[node_id]["properties"]["c_Meters"]) < 0.01:
                    if cityobject["attributes"]["startNode"] == "": 
                        cityobject["attributes"]["startNode"] = key
                    else:
                        cityobject["attributes"]["endNode"] = key
        cj["CityObjects"]["edge" + feature["id"]] = cityobject



    # Load polygon shapefile
    shape = fiona.open("../GIS/LoD1.shp")

    # Extract geometries
    checker = {}
    for feature in shape:
        if feature["properties"]["COR_CODE"] in checker:
            multisurface = []

            for coords in feature['geometry']['coordinates'][0]:
                cj["vertices"].append([coords[0], coords[1], coords[2]])
                multisurface.append(len(cj["vertices"]) -1)

            intid = feature["properties"]['INT_ID']
            semantics = {}
            if intid is None:
                    semantics["roadType"] = "Road"
            elif intid==1:
                semantics["IntersectionID"] = intid
                semantics["roadType"] = "Intersection"
            else:
                semantics["IntersectionID"] = intid
                semantics["roadType"] = "Roundabout"
                
            road_obj = cj["CityObjects"]["road" + str(feature["properties"]["COR_CODE"])]
            road_obj["geometry"][0]["boundaries"].append([multisurface])
            road_obj["geometry"][0]["semantics"]["surfaces"].append(semantics)
            road_obj["geometry"][0]["semantics"]["values"].append(
                len(road_obj["geometry"][0]["boundaries"])-1)

        else:
            checker[feature["properties"]["COR_CODE"]] = "added"
            
            multisurface = []
            cityobject = {"type": "Road", "geometry": []}
            geom = {"type": "MultiSurface",
                    "lod": 1,
                    "boundaries": [],
                    "semantics": {
                        "surfaces": [],
                        "values": [0]
                        }
                    }
            for coords in feature['geometry']['coordinates'][0]:
                cj["vertices"].append([coords[0], coords[1], coords[2]])
                multisurface.append(len(cj["vertices"]) -1)
            geom["boundaries"] = [[multisurface]]
            
            intid = feature["properties"]['INT_ID']
            semantics = {}
            if intid is None:
                    semantics["roadType"] = "Road"
            elif intid==1:
                semantics["IntersectionID"] = intid
                semantics["roadType"] = "Intersection"
            else:
                semantics["IntersectionID"] = intid
                semantics["roadType"] = "Roundabout"
                
            geom["semantics"]["surfaces"].append(semantics)
            geom["boundaries"] = [[multisurface]]
            cityobject["geometry"].append(geom)
            cj["CityObjects"]["road" + str(feature["properties"]["COR_CODE"])] = cityobject    

    # Add array of edges to geometry object
    for key in checker:
        edgelist = []
        for edge in lines:
            if edge["properties"]["COR_CODE"] == key:
                edgelist.append("edge"+ edge["id"])
        edgegeom = {"type": "RoadEdges",
                    "lod": 0.1,
                    "boundaries": edgelist,
                    }
        if len(edgelist) > 0:
            cj["CityObjects"]["road" + str(key)]["geometry"].append(edgegeom)
    
    
    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_LoD1_linked.json','w')
    fout.write(json_str)


if __name__ == '__main__':
    lod1linking()

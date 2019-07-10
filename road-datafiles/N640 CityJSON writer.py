import gdal
import shapely
import fiona
import json

extension_url = "https://github.com/fhb1990" \
                "/cityjson/blob/master/schema/v09/extensions/roadnetwork.json"

TrafficAreas = ['Rijstrook, Rijbaan Regionale weg (v)',
                'Rijstrook, Rijbaan Lokale weg (v)',
                'WGD Rijbaan - Lokale weg (v)',
                'WGD Rijbaan - Regionale weg (v)',
                'Linksafvak, Rijbaan Regionale weg (v)',
                'WGD Rijbaan - Lokale weg verkeersdrempel (v)'
                ]

def lod01writer():
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
                              }
                          }

            intid = feature["properties"]["INT_ID"]
            if intid is not None:
                cityobject["attributes"]["intersectionID"] = intid
                
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

                intid = feature["properties"]["INT_ID"]
                if intid is not None:
                    cityobject["attributes"]["intersectionID"] = intid

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
    shape = fiona.open('../GIS/LoD0.1.shp')

    # Extract geometries
    for feature in shape:
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
    
    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_Lod0.1.json','w')
    fout.write(json_str)


def lod02writer():
    # Load point shapefile
    punten = fiona.open("../GIS/Nodes_LoD0.2.shp")

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
                              }
                          }
            
            intid = feature["properties"]["INT_ID"]
            if intid is not None:
                cityobject["attributes"]["intersectionID"] = intid
            rntype = feature["properties"]["RoadNodeTy"]
            if rntype is not None:
                cityobject["attributes"]["roadNodeType"] = rntype
            else:
                cityobject["attributes"]["roadNodeType"] = "Attribute"
                
            geom = {"type": "MultiPoint",
                    "lod": 0.2,
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
                                  }
                              }
                intid = feature["properties"]["INT_ID"]
                if intid is not None:
                    cityobject["attributes"]["intersectionID"] = intid
                rntype = feature["properties"]["RoadNodeTy"]
                if rntype is not None:
                    cityobject["attributes"]["roadNodeType"] = rntype
                else:
                    cityobject["attributes"]["roadNodeType"] = "Attribute"

                geom = {"type": "MultiPoint",
                        "lod": 0.2,
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
    shape = fiona.open('../GIS/LoD0.2.shp')

    # Extract geometries
    for feature in shape:

        cityobject = {"type": "+RoadEdge",
                      "geometry": [],
                      "attributes": {
                          "startNode": "",
                          "endNode": "",
                          "edgeType": feature["properties"]["EDGETYPE"]
                          }
                      }

        intid = feature["properties"]["INT_ID"]
        if intid is not None:
            cityobject["attributes"]["intersectionID"] = intid
        func = feature["properties"]["Srt_strook"]
        if func is not None:
            cityobject["attributes"]["function"] = func
        stname = feature["properties"]["STT_NAAM"]
        if stname is not None:
            cityobject["attributes"]["streetName"] = stname
        admin = feature["properties"]["WEGBEHNAAM"]
        if admin is not None:
            cityobject["attributes"]["administrator"] = admin
        speed = feature["properties"]["MAXSNLHD"]
        if speed is not None:
            cityobject["attributes"]["maxSpeed"] = speed
        
        geom = {"type": "MultiLineString",
                "lod": 0.2,
                "boundaries": []}
        
        linestring = []
        for coords in feature['geometry']['coordinates']:
            cj["vertices"].append([coords[0], coords[1], coords[2]])
            linestring.append(len(cj["vertices"]) -1)
            
        geom["boundaries"] = [linestring]
        cityobject["geometry"].append(geom)
        
        for key in cj["CityObjects"]:
            if key.startswith("node"):
                if "edge" + feature["id"] in cj["CityObjects"][key]["attributes"]["edges"]:
                    if cityobject["attributes"]["startNode"] == "": 
                        cityobject["attributes"]["startNode"] = key
                    else:
                        cityobject["attributes"]["endNode"] = key
        cj["CityObjects"]["edge" + feature["id"]] = cityobject

    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_Lod0.2.json','w')
    fout.write(json_str)

def lod03writer():
    # Load point shapefile
    punten = fiona.open("../GIS/Nodes_LoD0.3.shp")

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
                              }
                          }
            
            intid = feature["properties"]["INT_ID"]
            if intid is not None:
                cityobject["attributes"]["intersectionID"] = intid
            rntype = feature["properties"]["RoadNodeTy"]
            if rntype is not None:
                cityobject["attributes"]["roadNodeType"] = rntype
            else:
                cityobject["attributes"]["roadNodeType"] = "Attribute"
                
            geom = {"type": "MultiPoint",
                    "lod": 0.3,
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
                                  }
                              }
                intid = feature["properties"]["INT_ID"]
                if intid is not None:
                    cityobject["attributes"]["intersectionID"] = intid
                rntype = feature["properties"]["RoadNodeTy"]
                if rntype is not None:
                    cityobject["attributes"]["roadNodeType"] = rntype
                else:
                    cityobject["attributes"]["roadNodeType"] = "Attribute"

                geom = {"type": "MultiPoint",
                        "lod": 0.3,
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
    shape = fiona.open('../GIS/LoD0.3.shp')

    # Extract geometries
    for feature in shape:

        cityobject = {"type": "+RoadEdge",
                      "geometry": [],
                      "attributes": {
                          "startNode": "",
                          "endNode": "",
                          "edgeType": feature["properties"]["EDGETYPE"]
                          }
                      }

        intid = feature["properties"]["INT_ID"]
        if intid is not None:
            cityobject["attributes"]["intersectionID"] = intid
        func = feature["properties"]["Srt_strook"]
        if func is not None:
            cityobject["attributes"]["function"] = func
        stname = feature["properties"]["STT_NAAM"]
        if stname is not None:
            cityobject["attributes"]["streetName"] = stname
        admin = feature["properties"]["WEGBEHNAAM"]
        if admin is not None:
            cityobject["attributes"]["administrator"] = admin
        speed = feature["properties"]["MAXSNLHD"]
        if speed is not None:
            cityobject["attributes"]["maxSpeed"] = speed
        
        geom = {"type": "MultiLineString",
                "lod": 0.3,
                "boundaries": []}
        
        linestring = []
        for coords in feature['geometry']['coordinates']:
            cj["vertices"].append([coords[0], coords[1], coords[2]])
            linestring.append(len(cj["vertices"]) -1)
            
        geom["boundaries"] = [linestring]
        cityobject["geometry"].append(geom)
        
        for key in cj["CityObjects"]:
            if key.startswith("node"):
                if "edge" + feature["id"] in cj["CityObjects"][key]["attributes"]["edges"]:
                    if cityobject["attributes"]["startNode"] == "": 
                        cityobject["attributes"]["startNode"] = key
                    else:
                        cityobject["attributes"]["endNode"] = key
        cj["CityObjects"]["edge" + feature["id"]] = cityobject

    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_Lod0.3.json','w')
    fout.write(json_str)


def lod1writer():
    # Load shapefile
    shape = fiona.open("../GIS/LoD1.shp")

    # Initialize CityJSON file
    cj = {}
    cj["type"] = "CityJSON"
    cj["version"] = "1.0"
    cj["extensions"] = {"RoadExt" : {"url": extension_url, "version": 1.0}}
    cj["CityObjects"] = {}
    cj["vertices"] = []

    # Extract geometries

    for feature in shape:
        cityobject = {"type": "Road", "geometry": []}
        geom = {"type": "MultiSurface",
                "lod": 1,
                "boundaries": [],
                "semantics": {
                    "surfaces": [],
                    "values": [0]
                    }
                }

        multisurface = []
        for coords in feature['geometry']['coordinates'][0]:
            cj["vertices"].append([coords[0], coords[1], coords[2]])
            multisurface.append(len(cj["vertices"]) -1)
        geom["boundaries"] = [[multisurface]]

        intid = feature["properties"]['INT_ID']
        semantics = {}
        if intid is None:
            semantics["roadType"] = "Road"
        elif intid == 1:
            semantics["IntersectionID"] = intid
            semantics["roadType"] = "Intersection"
        else:
            semantics["IntersectionID"] = intid
            semantics["roadType"] = "Roundabout"
        
        geom["semantics"]["surfaces"].append(semantics)
        geom["boundaries"] = [[multisurface]]
        cityobject["geometry"].append(geom)
        i_d = str(feature["properties"]['OBJECTID'])
        cj["CityObjects"]["road" + i_d] = cityobject


    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_LoD1.json','w')
    fout.write(json_str)



def lod2writer():
    # Load shapefile
    shape = fiona.open("../GIS/LoD2.shp")

    # Initialize CityJSON file
    cj = {}
    cj["type"] = "CityJSON"
    cj["version"] = "1.0"
    cj["extensions"] = {"RoadExt" : {"url": extension_url, "version": 1.0}}
    cj["CityObjects"] = {}
    cj["vertices"] = []

    # Extract geometries

    for feature in shape:
        cityobject = {"type": "Road", "geometry": []}
        geom = {"type": "MultiSurface",
                "lod": 2,
                "boundaries": [],
                "semantics": {
                    "surfaces": [],
                    "values": [0]
                    }
                }

        multisurface = []
        for coords in feature['geometry']['coordinates'][0]:
            cj["vertices"].append([coords[0], coords[1], coords[2]])
            multisurface.append(len(cj["vertices"]) -1)
        geom["boundaries"] = [[multisurface]]

        func = feature["properties"]['OBJCOD_OMS']
        intid = feature["properties"]['INT_ID']
        if func in TrafficAreas:
            semantics = {"type": "TrafficArea"}
            if intid is None:
                semantics["roadType"] = "Carriageway"
                semantics["function"] = func
            elif intid == 1:
                semantics["roadType"] = "Intersection"
                semantics["function"] = func
                semantics["intersectionID"] = intid
            else:
                semantics["roadType"] = "Roundabout"
                semantics["function"] = func
                semantics["intersectionID"] = intid
        else:
            semantics = {"type": "AuxiliaryTrafficArea"}
        
        admin = feature["properties"]['BRONHOUD_1']
        if admin is not None:
            semantics["administrator"] = admin
        
        geom["semantics"]["surfaces"].append(semantics)
        geom["boundaries"] = [[multisurface]]
        cityobject["geometry"].append(geom)
        i_d = str(feature["properties"]['OBJECTID'])
        cj["CityObjects"]["road" + i_d] = cityobject


    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_LoD2.json','w')
    fout.write(json_str)



def lod3writer():
    # Load shapefile
    shape = fiona.open("../GIS/LoD3.shp")

    # Initialize CityJSON file
    cj = {}
    cj["type"] = "CityJSON"
    cj["version"] = "1.0"
    cj["extensions"] = {"RoadExt" : {"url": extension_url, "version": 1.0}}
    cj["CityObjects"] = {}
    cj["vertices"] = []

    # Extract geometries

    for feature in shape:
        cityobject = {"type": "Road", "geometry": []}
        geom = {"type": "MultiSurface",
                "lod": 3,
                "boundaries": [],
                "semantics": {
                    "surfaces": [],
                    "values": [0]
                    }
                }

        multisurface = []
        for coords in feature['geometry']['coordinates'][0]:
            cj["vertices"].append([coords[0], coords[1], coords[2]])
            multisurface.append(len(cj["vertices"]) -1)
        geom["boundaries"] = [[multisurface]]

        func = feature["properties"]['OBJCOD_OMS']
        intid = feature["properties"]['INT_ID']
        if func in TrafficAreas:
            semantics = {"type": "TrafficArea"}
            if intid is None:
                semantics["roadType"] = "Lane"
            elif intid == 1:
                semantics["roadType"] = "Intersection"
                semantics["intersectionID"] = intid
            else:
                semantics["roadType"] = "Roundabout"
                semantics["intersectionID"] = intid
        else:
            semantics = {"type": "AuxiliaryTrafficArea"}
        semantics["function"] = func
        admin = feature["properties"]['BRONHOUD_1']
        if admin is not None:
            semantics["administrator"] = admin
        
        geom["semantics"]["surfaces"].append(semantics)
        geom["boundaries"] = [[multisurface]]
        cityobject["geometry"].append(geom)
        i_d = str(feature["properties"]['OBJECTID'])
        cj["CityObjects"]["road" + i_d] = cityobject


    # Write CityJSON file
    json_str = json.dumps(cj, indent=2)
    fout = open('N640_LoD3.json','w')
    fout.write(json_str)


if __name__ == '__main__':
    lod01writer()
    lod02writer()
    lod03writer()
    lod1writer()
    lod2writer()
    lod3writer()


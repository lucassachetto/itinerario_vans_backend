import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph
import geopy.distance
import numpy as np


def centro_circulo(coord_list):
    
    coord_rad = np.radians(coord_list)

    
    centro = np.mean(coord_rad, axis=0)

    centro_graus = np.degrees(centro)

    raio = max(geopy.distance.geodesic(centro_graus, coord).meters for coord in coord_list)

    return centro_graus.tolist(), raio

def calcula_rota(origCoords, destCoord, stepCoords):
    orig = (origCoords[0], origCoords[1])
    dest = (destCoord[0], destCoord[1])
    allCoords = [orig, dest]
    steps = []
    
    for stepCoord in stepCoords:
        steps.append((stepCoord[0], stepCoord[1]))
        allCoords.append((stepCoord[0], stepCoord[1]))

    centro, raio = centro_circulo(allCoords)

    G = ox.graph_from_point(centro, dist=raio+100, dist_type="bbox", network_type="drive")

    hwy_speeds = {"unclassified": 20}
    G = ox.add_edge_speeds(G, hwy_speeds)
    G = ox.add_edge_travel_times(G)

    color_map = []

    nodeOrig = ox.nearest_nodes(G, orig[1], orig[0])
    nodeDest = ox.nearest_nodes(G, dest[1], dest[0])
    stepsNodes = []

    for step in steps:
        stepsNodes.append(ox.nearest_nodes(G, step[1], step[0]))

    for node in G:
        if (node == nodeOrig):
            color_map.append('blue')
        elif (node == nodeDest):
            color_map.append('green')
        elif (node in stepsNodes):
            color_map.append('yellow')
        else:
            color_map.append('red')

    #plot graph
    #fig, ax = ox.plot_graph(G, node_color=color_map)

    #Pega tempo de percurso entre todos os nós
    travel_time_dict = dict(nx.floyd_warshall(G, 'travel_time'))

    stepNodesToDestiny = {}

    for node in stepsNodes:
        stepNodesToDestiny[node] = travel_time_dict[node][nodeDest]
        
    stepNodesOrder = sorted(stepNodesToDestiny.items(), key=lambda x:x[1])
    paths = []

    # Origem para o passageiro mais longe, usando o algoritimo de Djikstra's
    paths.append(ox.shortest_path(G, nodeOrig, stepNodesOrder[len(stepNodesOrder) -1][0], weight="travel_time"))

    i = len(stepNodesOrder) -1

    while i >= 1:
        paths.append(ox.shortest_path(G, stepNodesOrder[i][0], stepNodesOrder[i - 1][0], weight="travel_time"))
        i = i-1

    paths.append(ox.shortest_path(G, stepNodesOrder[0][0], nodeDest, weight="travel_time"))

    resultCoords = []

    for i in range(0, len(paths)):
        resultCoords.append([])
        for node in paths[i]:
            resultCoords[len(resultCoords)-1].append(G.nodes[node])

    return resultCoords

    #fig, ax = ox.plot_graph_routes(G, paths, route_color="y", route_linewidth=2, node_size=10)


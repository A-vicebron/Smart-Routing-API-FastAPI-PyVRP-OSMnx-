import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt


G = ox.graph_from_place("Nikaia, Greece", network_type="drive")
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)


coordinates = {
    "Depot": (37.9657507, 23.6473298),      
    "Bin 1": (39.5615492, 22.4620466),      
    "Bin 2": (37.9762057, 23.6710114)       
}


nodes = {name: ox.distance.nearest_nodes(G, lon, lat) for name, (lat, lon) in coordinates.items()}

# Υπολογισμός διαδρομών
route1 = nx.shortest_path(G, nodes["Depot"], nodes["Bin 1"], weight="travel_time")
route2 = nx.shortest_path(G, nodes["Depot"], nodes["Bin 2"], weight="travel_time")


fig, ax = ox.plot_graph_routes(
    G,
    routes=[route1, route2],
    route_colors=["red", "blue"],
    route_linewidth=4,
    node_size=0,
    bgcolor="white"
)

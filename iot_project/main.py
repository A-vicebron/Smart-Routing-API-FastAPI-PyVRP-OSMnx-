import osmnx as ox
import networkx as nx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from geopy.geocoders import Nominatim
from pyvrp import Model, Result
from pyvrp.stop import MaxRuntime

# -------------------  travel time  -------------------
globalG = ox.graph_from_place("Nikaia, Greece", network_type="drive")
globalG = ox.add_edge_speeds(globalG)
globalG = ox.add_edge_travel_times(globalG)

# ------------------- FastAPI -------------------
app = FastAPI()

# -------------------Classes -------------------
class Location(BaseModel):
    latitude: float
    longitude: float

class CollectionPoint(BaseModel):
    name: str
    location: str
    capacity: int

class Truck(BaseModel):
    name: str
    capacity: int

class RequestObject(BaseModel):
    truck_station: dict
    collection_points: List[CollectionPoint]
    trucks: List[Truck]

class Path(BaseModel):
    truck: Truck
    route: List[CollectionPoint]

class ResponseObject(BaseModel):
    paths: List[Path]

# ------------------- BONUS 2: Global cache -------------------
geocode_cache = {}

# ------------------- BONUS 1: Travel time from OpenStreetMap -------------------
def get_travel_time(coord1: Location, coord2: Location) -> float:
    print(f"🛰️ Υπολογισμός travel time από {coord1} προς {coord2}")
    src = ox.distance.nearest_nodes(globalG, coord1.longitude, coord1.latitude)
    dst = ox.distance.nearest_nodes(globalG, coord2.longitude, coord2.latitude)
    return nx.shortest_path_length(globalG, src, dst, weight="travel_time")

# ------------------- Endpoint VRP -------------------
@app.post("/find_routes", response_model=ResponseObject)
def solve_vrrp(request: RequestObject) -> ResponseObject:
    geolocator = Nominatim(user_agent="iot_project")
    coordinates = {}

    # GIS (with cache)
    for cp in request.collection_points:
        address = cp.location
        if address not in geocode_cache:
            print(f"🌐 Geocoding για: {address}")
            loc = geolocator.geocode(address)
            if loc is None:
                raise ValueError(f"🚫 Δεν βρέθηκε η τοποθεσία για: {cp.name} - {address}")
            geocode_cache[address] = loc
        else:
            print(f"📦 Cache hit για: {address}")
        loc = geocode_cache[address]
        coordinates[cp.name] = Location(latitude=loc.latitude, longitude=loc.longitude)

    # GIS STATIONS (με cache)
    station_address = request.truck_station["location"]
    if station_address not in geocode_cache:
        print(f"🌐 Geocoding για: {station_address}")
        station_loc = geolocator.geocode(station_address)
        if station_loc is None:
            raise ValueError(f"🚫 Δεν βρέθηκε η τοποθεσία για τον σταθμό: {station_address}")
        geocode_cache[station_address] = station_loc
    else:
        print(f"📦 Cache hit για: {station_address}")
    station = geocode_cache[station_address]
    coordinates["Source"] = Location(latitude=station.latitude, longitude=station.longitude)

    # CREATE MODEL VRP
    m = Model()
    m.add_depot(x=station.latitude, y=station.longitude)

    clients = []
    for cp in request.collection_points:
        loc = coordinates[cp.name]
        travel_time = get_travel_time(coordinates["Source"], loc)
        print(f"🕒 Travel time έως {cp.name}: {travel_time:.2f} δευτερόλεπτα")

        client = m.add_client(
            x=loc.latitude,
            y=loc.longitude,
            delivery=cp.capacity
            # service_time=travel_time  # αν το υποστήριζε το API
        )
        clients.append(client)

    # ADD TRUCKS
    for truck in request.trucks:
        m.add_vehicle_type(capacity=truck.capacity)

    # RESOLVE
    res: Result = m.solve(stop=MaxRuntime(5 + len(clients) / 2), display=False)

    #  CREATE RESPONSE
    response = ResponseObject(paths=[
        Path(
            truck=request.trucks[i],
            route=[request.collection_points[c - 1] for c in route]
        )
        for i, route in enumerate(res.best.routes())
    ])

    return response






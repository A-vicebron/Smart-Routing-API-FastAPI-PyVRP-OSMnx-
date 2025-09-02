import requests

url = "http://127.0.0.1:8000/find_routes"

# ENTRY DATA
data = {
    "truck_station": {
        "location": "Nikaia, Greece"
    },
    "collection_points": [
        {
            "name": "Bin 1",
            "location": "Agiou Georgiou 2, Nikaia",
            "capacity": 5
        },
        {
            "name": "Bin 2",
            "location": "Petrou Ralli 120, Nikaia",
            "capacity": 7
        }
    ],
    "trucks": [
        {
            "name": "Truck A",
            "capacity": 10
        },
        {
            "name": "Truck B",
            "capacity": 10
        }
    ]
}

# SEND POST REQUEST
response = requests.post(url, json=data)

# RESULTS
if response.status_code == 200:
    result = response.json()
    print("📦 Απάντηση από server:")
    for path in result["paths"]:
        print(f"🚛 {path['truck']['name']}")
        for stop in path["route"]:
            print(f"   🗑️ {stop['name']} - {stop['location']}")
else:
    print(f"❌ Σφάλμα: {response.status_code}")
    print(response.text)

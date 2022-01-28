# shows how API can be used to extract start and end stations of all railways
import requests

response = requests.get("http://127.0.0.1:5000/get-railways")

print(response.json())  # = alle railways mit Gesamtinformation

railways = response.json()

# Für jede Strecke Start- und Endstation ausgeben
for railway in railways:
    print(f"{railway['name']} hat")
    if len(railway["sections"]) > 0:
        start_station = railway["sections"][0]["start_station"]["name"]
        end_station = railway["sections"][-1]["end_station"]["name"]
        print(f"-Start: {start_station}")
        print(f"-Ende: {end_station}")
    else:
        print("-weder Start noch ein Ende")
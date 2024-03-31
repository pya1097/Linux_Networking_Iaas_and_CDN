from flask import Flask, request, jsonify
import json, random

app = Flask(__name__)


with open('../database/mapping.json', 'r') as file:
    proximity = json.load(file)

with open("../database/dns_database.json", "r") as file:
    database = json.load(file)

# Route to handle client requests
@app.route("/", methods=["GET"])
def handle_request():
    website = request.args.get("website")
    user_location = request.args.get("location")

    server_location = proximity[user_location]
    if website in database:
        dst_list = []
        for  loc in database[website]:
            if server_location.lower() in loc.lower():
                dst_list.append(database[website][server_location])
        
        ip_address, port_number = random.choice(dst_list)
        return jsonify({website: {server_location: (port_number, ip_address)}})
    else:
        return jsonify({"error": "No matching data found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
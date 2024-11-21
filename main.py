from flask import Flask, request, jsonify, render_template
import requests
import os
from urllib.parse import quote

app = Flask(__name__)

# Function to get latitude and longitude from location name
def get_lat_lon(location_name):
    api_key = os.getenv('AIzaSyDO6E4Msd7z88zedmlY48YCz47LQVmHuAA')  # Ensure the correct environment variable is set
    if not api_key:
        return None, None

    encoded_location = quote(location_name)  # Encoding the location to handle spaces and special characters
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_location}&key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            return None, None
    except requests.RequestException as e:
        print(f"Error fetching geocode data: {e}")
        return None, None

# Root route to serve the map page
@app.route('/')
def map_page():
    return render_template('map.html')

# Route to get coordinates
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400

    lat, lon = get_lat_lon(location)
    if lat is None or lon is None:
        return jsonify({"error": "Location not found", "message": f"Could not find coordinates for '{location}'"}), 404

    return jsonify({"location": location, "coordinates": {"latitude": lat, "longitude": lon}})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "The requested endpoint does not exist"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "The method is not allowed for this endpoint"}), 405

# Error handler for internal server errors (500)
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)

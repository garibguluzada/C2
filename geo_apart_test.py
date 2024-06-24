import geocoder
import requests
import json

def get_geolocation_info():
    try:
        # Get the geolocation of the current IP address
        g = geocoder.ip('me')
        ip_address = 'me'
        request_url = 'https://geolocation-db.com/jsonp/' + ip_address
        response = requests.get(request_url)
        result = response.content.decode()
        result = result.split("(")[1].strip(")")
        result = json.loads(result)
        result["postal"] = g.postal
        result["state"] = g.state
        result["city"] = g.city

        # Print the result dictionary with indentation for better readability
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_geolocation_info()
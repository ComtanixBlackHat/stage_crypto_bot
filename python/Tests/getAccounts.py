
import requests
import json
import time
import base64
import hashlib
import hmac

# Load API credentials securely (avoid hardcoding)
API_KEY = "Sc1rIvjDK4LaNzmQ7IfcrjlfLtRP7l2DyXuQK62gM6vTTghHQgcaL2PZ"
API_SECRET = "wsQzohrIl6SUX0sUa10uWO7iPQ+T5mc4q4YjubYXOq1jgyWnZum1Wj8nncj/WajsVXt9SUj9iBOhhduJ5Vf/jw=="

API_URL = "https://api.kraken.com"
ENDPOINT = "/0/private/Balance"

# Generate a nonce (must be unique and increasing)
nonce = str(int(time.time() * 1000))

# Prepare payload
payload = {
    "nonce": nonce
}
encoded_payload = json.dumps(payload)

# Compute the API signature
def get_kraken_signature(url_path, data, secret):
    postdata = data.encode()
    nonce_bytes = nonce.encode()
    
    # Concatenate nonce and postdata
    sha256_hash = hashlib.sha256(nonce_bytes + postdata).digest()
    
    # Decode secret and generate HMAC-SHA512 signature
    secret_decoded = base64.b64decode(secret)
    hmac_key = hmac.new(secret_decoded, url_path.encode() + sha256_hash, hashlib.sha512)
    
    return base64.b64encode(hmac_key.digest()).decode()

# Generate API-Sign
api_sign = get_kraken_signature(ENDPOINT, encoded_payload, API_SECRET)

# Headers
headers = {
    'API-Key': API_KEY,
    'API-Sign': api_sign,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Send the request
response = requests.post(API_URL + ENDPOINT, headers=headers, data=encoded_payload)

# Print response
print(response.json())

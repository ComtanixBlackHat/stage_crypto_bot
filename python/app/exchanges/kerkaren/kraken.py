import requests

class Kraken:
    @staticmethod
    def get_symbols():
        url = 'https://api.kraken.com/0/public/AssetPairs'
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error if the request fails
            
            # Extracting the result from the response
            data = response.json()
            
            # Check if the response contains an error
            if data['error']:
                return {'error': 'Failed to retrieve symbols'}
            
            # Extract the symbol names from the result
            symbols = list(data['result'].keys())
            
            return {'symbols': symbols}
        
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

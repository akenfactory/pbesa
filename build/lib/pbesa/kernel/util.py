# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 4.0.0
@date 09/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import uuid
import base64
import requests

# --------------------------------------------------------
# Define generate short uuid
# --------------------------------------------------------

def generate_short_uuid(length=5):
    # Generate a UUID
    uuid_str = str(uuid.uuid4())
    
    # Encode UUID to bytes
    uuid_bytes = uuid.UUID(uuid_str).bytes
    
    # Encode bytes to base64 and strip non-alphanumeric characters
    base64_str = base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')
    
    # Return a substring of the desired length
    short_uuid = base64_str[:length]
    short_uuid.replace('_', 'A')
    short_uuid.replace('-', 'B')
    short_uuid.replace('=', 'C')
    return short_uuid.lower()

# --------------------------------------------------------
# Define API interface
# --------------------------------------------------------

class APIClient:
    """API Client"""

    def __init__(self, base_url, headers=None, timeout=120, access_token=None) -> None:
        """ Initialize the API client with the given base URL, headers, and timeout.
        @param base_url: Base URL for the API.
        @param headers: Headers to include in the API requests.
        @param timeout: Timeout for the API requests.
        @param access_token: Access token to include in the headers.
        """
        self.base_url = base_url
        self.headers = headers if headers else {
            'Content-Type': 'application/json',
        }
        self.timeout = timeout
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
    
    def post(self, endpoint, payload) -> dict:
        """
        Make a POST request to the specified endpoint with the given data.
        :param endpoint: Endpoint to send the POST request to.
        :param payload: Data to include in the POST request.
        :return: Response object if the request is successful, None otherwise.
        """
        response = None
        try:
            response = requests.post(
                url=f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            print(f"POST request to {endpoint} succeeded: {response.status_code}")
            res = {
                "status": True,
                "message": response.json()
            }
            return res
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")
        if response is not None:
            return {
                "status": False,
                "message": response.text
            }
        return {
            "status": False,
            "message": "An error occurred while making the POST request."
        }
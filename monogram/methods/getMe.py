from typing import Union
from monogram import Monogram, validate_payload

class getMe(Monogram):
    def __new__(cls) -> dict:
        payload = validate_payload(locals().copy())
        # send post request to telegram based on method sendMessage, Construct the API endpoint URL
        response = cls.request(cls, method='getMe', data=payload, res=True)
        return response.json()
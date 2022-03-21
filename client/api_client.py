import json
import requests
import logging

from requests import HTTPError, ConnectionError

from config_manager import server_url, server_port, server_endpoint

_uri = server_url + ":" + server_port + server_endpoint


def send_data(payload: dict):
    try:
        logging.info(f"sending payload = {payload} to {_uri}")
        response = requests.post(url=_uri, data=json.dumps(payload))
        logging.info(f"response text: {response.text}")
    except ConnectionError:
        logging.warning(f"sending payload = {payload} to {_uri} failed")
    except HTTPError as error:
        logging.error(f"HTTP Error ({_uri}) payload = {payload}, {error}")

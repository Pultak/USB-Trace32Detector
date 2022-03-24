import json
import requests
import logging
from time import sleep
from diskcache import Deque
from requests import HTTPError, ConnectionError

from config_manager import server_url, server_port, server_endpoint, cache_dir, cache_retry_period_seconds, cache_max_retries, cache_max_entries


_cache = Deque(directory=cache_dir)
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


def api_client_run():
    while True:
        sleep(cache_retry_period_seconds)

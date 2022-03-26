import json
import requests
import logging
from time import sleep
from diskcache import Deque
from requests import HTTPError, ConnectionError

from config_manager import server_url, server_port, server_endpoint, cache_dir, \
    cache_retry_period_seconds, cache_max_retries, cache_max_entries


_cache = Deque(directory=cache_dir)
_uri = server_url + ":" + server_port + server_endpoint


def send_data(payload: dict):
    try:
        logging.info(f"sending payload = {payload} to {_uri}")
        response = requests.post(url=_uri, data=json.dumps(payload))
        logging.info(f"response text: {response.text}")
    except ConnectionError:
        logging.warning(f"sending payload = {payload} to {_uri} failed")
        _cache_failed_payload(payload)
    except HTTPError as error:
        logging.error(f"HTTP Error ({_uri}) payload = {payload}, {error}")
        _cache_failed_payload(payload)


def _cache_failed_payload(payload: dict):
    if len(_cache) >= cache_max_entries:
        oldest_payload = _cache.pop()
        logging.warning(f"cache is full - discarding payload = {oldest_payload}")

    logging.info(f"adding payload = {payload} into cache")
    _cache.append(payload)


def api_client_run():
    while True:
        retries = min(cache_max_retries, len(_cache))
        logging.info(f"emptying the cache ({retries} records)")
        for _ in range(0, retries):
            payload = _cache.pop()
            send_data(payload)
        sleep(cache_retry_period_seconds)

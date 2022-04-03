import json
import requests
import logging
from time import sleep
from diskcache import Deque
from requests import HTTPError, ConnectionError


_uri = None
_cache = None
_config = None


def api_client_set_config(config):
    global _config, _cache, _uri
    _config = config
    _cache = Deque(directory=_config.cache_dir)
    _uri = config.server_url + ":" + config.server_port + config.server_endpoint


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
    if len(_cache) >= _config.cache_max_entries:
        oldest_payload = _cache.pop()
        logging.warning(f"cache is full - discarding payload = {oldest_payload}")

    logging.info(f"adding payload = {payload} into cache")
    _cache.append(payload)


def _resend_cached_payloads():
    retries = min(_config.cache_max_retries, len(_cache))
    logging.info(f"emptying the cache ({retries} records)")
    for _ in range(0, retries):
        payload = _cache.pop()
        send_data(payload)


def api_client_run():
    while True:
        _resend_cached_payloads()
        sleep(_config.cache_retry_period_seconds)

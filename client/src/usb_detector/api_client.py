import json
import requests
import logging
from time import sleep
from diskcache import Deque
from requests import HTTPError, ConnectionError
from requests.exceptions import InvalidSchema


_uri = None     # server uri (url, port, and endpoint)
_cache = None   # cache (failed payloads)
_config = None  # instance of Config


def api_client_set_config(config):
    """Initializes the client API module.

    This function is meant to be called prior to calling any other function
    of the API module. It stores the instance of Config (config manager)
    into a private variable. It also initializes the cache for unsuccessful
    payloads and constructs a URI (endpoint on the server side).

    :param config: instance of Config which holds all values defined
                   in the configuration file.
    """
    # Store the variables globally within the module (file).
    global _config, _cache, _uri

    # Store the instance of Config and initialize the cache.
    _config = config
    _cache = _init_cache()

    # Creates the URI which is made of the server url, port, and path (endpoint).
    _uri = config.server_url + ":" + config.server_port + config.server_endpoint


def _init_cache():
    """ Initializes and returns a disk-based cache.

    The cache holds payloads that the application failed
    to send to the server. It periodically attempts to resent
    them to the server. All parameters can be seen in the
    configuration file.

    :return: instance of a new cache (Deque - FIFO)
    """
    return Deque(directory=_config.cache_dir)


def send_data(payload: dict):
    """Sends a payload off to the server.

    This function is called whenever a USB is connected
    or disconnected. If there is no internet connection or the
    server is not up and running, the payload will be stored
    into the disk cache.

    :param payload:
    """
    # Make sure that the URI has been constructed properly.
    # It's supposed to be done by calling the api_client_set_config function
    # with appropriate parameters.
    if _uri is None:
        logging.warning(f"sending payload = {payload} failed because uri is set to None")
        _cache_failed_payload(payload)
        return
    try:
        logging.info(f"sending payload = {payload} to {_uri}")
        response = requests.post(url=_uri, data=json.dumps(payload))
        logging.info(f"response text: {response.text}")
    except (ConnectionError, InvalidSchema):
        logging.warning(f"sending payload = {payload} to {_uri} failed")
        _cache_failed_payload(payload)
    except HTTPError as error:
        logging.error(f"HTTP Error ({_uri}) payload = {payload}, {error}")
        _cache_failed_payload(payload)


def _cache_failed_payload(payload: dict):
    """ Caches a payload.

    This function is called when the application fails to send a payload
    to the server. The payload gets stored into a file-based cache from which
    it will be periodically retrieved as the client will attempt to send
    it to the server again. All parameters regarding the cache can be found
    in the configuration file.

    :param payload: payload to be cached
    """
    # If the cache is "full", discard the oldest record.
    if len(_cache) >= _config.cache_max_entries:
        oldest_payload = _cache.pop()
        logging.warning(f"cache is full - discarding payload = {oldest_payload}")

    # Store the payload into the cache.
    logging.info(f"adding payload = {payload} into cache")
    _cache.append(payload)


def _resend_cached_payloads():
    """Reattempts to send cached payloads to the server (API).

    In the configuration file, there is a predefined number of
    payloads that can be sent to the server with each call of this function.
    This function is called periodically from api_client_run in order
    to resend failed payloads to the server.

    """
    # Calculate how many payload will be sent to the server
    retries = min(_config.cache_max_retries, len(_cache))
    logging.info(f"emptying the cache ({retries} records)")

    # Send the payloads to the server one by one.
    for _ in range(0, retries):
        payload = _cache.pop()
        send_data(payload)


def api_client_run():
    """ Keeps resending failed payloads to the server.

    This function is instantiated as a thread that periodically
    calls the _resend_cached_payloads function in order to empty
    the cache (failed payloads). The period can be set in the
    configuration file.
    """
    while True:
        # Resend a predefined amount of failed payloads to the server.
        _resend_cached_payloads()

        # Sleep for a predefined amount of seconds.
        sleep(_config.cache_retry_period_seconds)

import httpx
from httpx import Auth
from typing import Optional, Dict, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from ppp_connectors.helpers import setup_logger, combine_env_configs
from functools import wraps
import inspect


def log_method_call(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        caller = func.__name__
        sig = inspect.signature(func)
        bound = sig.bind(self, *args, **kwargs)
        bound.apply_defaults()
        query_value = bound.arguments.get("query")
        self._log(f"{caller} called with query: {query_value}")
        return func(self, *args, **kwargs)
    return wrapper

class Broker:
    """
    A base HTTP client that provides structured request handling, logging, retries, and optional environment config loading.
    Designed to be inherited by specific API connector classes.

    Attributes:
        base_url (str): The base URL of the API.
        headers (Dict[str, str]): Default headers for all requests.
        enable_logging (bool): Whether to enable logging for requests.
        enable_backoff (bool): Whether to apply exponential backoff on request failures.
        timeout (int): Timeout for HTTP requests in seconds.
        env_config (Dict[str, Any]): Environment variables loaded from .env and os.environ if enabled.
    """
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        enable_logging: bool = False,
        enable_backoff: bool = False,
        timeout: int = 10,
        load_env_vars: bool = False
    ):
        self.base_url = base_url.rstrip('/')
        self.logger = setup_logger(self.__class__.__name__) if enable_logging else None
        self.enable_backoff = enable_backoff
        self.timeout = timeout
        self.session = httpx.Client(timeout=timeout)
        self.headers = headers or {}
        self.env_config = combine_env_configs() if load_env_vars else {}

    def _log(self, message: str):
        """
        Internal logging helper. Logs message if logging is enabled.
        """
        if self.logger:
            self.logger.info(message)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        auth: Optional[Union[tuple, Auth]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_kwargs: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Construct and execute an HTTP request with optional retries.

        Args:
            method (str): HTTP method ('GET', 'POST', etc.)
            endpoint (str): The API path (joined with base_url).
            params (Optional[Dict[str, Any]]): Query parameters for the request.
            json (Optional[Dict[str, Any]]): JSON body for the request.
            auth (Optional[tuple]): Optional basic auth tuple (username, password).
            retry_kwargs (Optional[Dict[str, Any]]): Optional overrides for retry behavior.

        Returns:
            httpx.Response: The HTTP response object.

        Raises:
            RetryError: If the request fails after retries.
            httpx.HTTPStatusError: If the response status code indicates an error.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_fn = self.session.request

        if self.enable_backoff:
            request_fn = retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                reraise=True,
                **(retry_kwargs or {}),
            )(request_fn)

        try:
            response = request_fn(
                method=method,
                url=url,
                headers=headers or self.headers,
                params=params,
                json=json,
                auth=auth,
            )
            response.raise_for_status()
            return response
        except RetryError as re:
            self._log(f"Retry failed: {re.last_attempt.exception()}")
            raise
        except httpx.HTTPStatusError as he:
            self._log(f"HTTP error: {he}")
            raise

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Convenience method for HTTP GET requests.

        Args:
            endpoint (str): API endpoint path.
            params (Optional[Dict[str, Any]]): Optional query parameters.

        Returns:
            httpx.Response: The HTTP response object.
        """
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Convenience method for HTTP POST requests.

        Args:
            endpoint (str): API endpoint path.
            json (Optional[Dict[str, Any]]): Optional JSON payload.

        Returns:
            httpx.Response: The HTTP response object.
        """
        return self._make_request("POST", endpoint, json=json, **kwargs)
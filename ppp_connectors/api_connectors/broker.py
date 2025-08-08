import httpx
from httpx import Auth
from typing import Optional, Dict, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from ppp_connectors.helpers import setup_logger, combine_env_configs
from functools import wraps
import inspect
import os


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
        load_env_vars (Dict[str, Any]): Environment variables loaded from .env and os.environ if enabled.
        proxy (Optional[str]): Single proxy URL passed to HTTPX via the `proxy` parameter.
        mounts (Optional[Dict[str, httpx.HTTPTransport]]): Per-scheme proxy routing, e.g., {"http://": httpx.HTTPTransport(proxy=...), "https://": httpx.HTTPTransport(proxy=...)}.
        trust_env (bool): Whether to allow HTTPX to read proxy and other settings from environment variables (HTTP(S)_PROXY, NO_PROXY, etc.).

        When `load_env_vars=True`, `.env` values from `combine_env_configs()` are considered for proxy resolution even
        if they are not present in the real OS environment. If both `.env` and OS env define a value, OS env wins.

        Note: Proxy settings are applied when the client is constructed and remain fixed for the
        lifetime of the instance. To change proxies or `trust_env`, re‑instantiate the connector.

        Additionally, extra `httpx.Client` keyword arguments can be passed to the constructor via
        `**client_kwargs` (e.g., `verify=False`, `http2=True`, custom transports). These are forwarded
        to the underlying `httpx.Client` when the session is created. Per-request options can also be
        supplied to `get`/`post` and will be forwarded to `httpx.Client.request`.
    """
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        enable_logging: bool = False,
        enable_backoff: bool = False,
        timeout: int = 10,
        load_env_vars: bool = False,
        proxy: Optional[str] = None,
        mounts: Optional[Dict[str, httpx.HTTPTransport]] = None,
        trust_env: bool = True,
        **client_kwargs,
    ):
        self.base_url = base_url.rstrip('/')
        self.logger = setup_logger(self.__class__.__name__) if enable_logging else None
        self.enable_backoff = enable_backoff
        self.timeout = timeout
        self.headers = headers or {}
        self.env_config = combine_env_configs() if load_env_vars else {}
        self._client_kwargs = dict(client_kwargs) if client_kwargs else {}

        # Determine proxy configuration (HTTPX uses `proxy` or per-scheme `mounts`).
        # Priority: mounts > proxy > env source (.env via self.env_config, else os.environ when trust_env=True) > none
        self.proxy = proxy
        self.mounts = mounts
        self.trust_env = trust_env

        if self.mounts:
            # Per-scheme routing wins
            client_options = dict(self._client_kwargs)
            client_options.pop("timeout", None)
            self.session = httpx.Client(timeout=timeout, mounts=self.mounts, trust_env=self.trust_env, **client_options)
        elif self.proxy:
            # Single proxy URL
            client_options = dict(self._client_kwargs)
            client_options.pop("timeout", None)
            self.session = httpx.Client(timeout=timeout, proxy=self.proxy, trust_env=self.trust_env, **client_options)
        else:
            # Try to resolve proxies from env sources (.env if loaded, else OS env if trust_env=True)
            env_proxy, env_mounts = self._collect_proxy_config()
            if env_mounts:
                self.mounts = env_mounts
                client_options = dict(self._client_kwargs)
                client_options.pop("timeout", None)
                self.session = httpx.Client(timeout=timeout, mounts=self.mounts, trust_env=self.trust_env, **client_options)
            elif env_proxy:
                self.proxy = env_proxy
                client_options = dict(self._client_kwargs)
                client_options.pop("timeout", None)
                self.session = httpx.Client(timeout=timeout, proxy=self.proxy, trust_env=self.trust_env, **client_options)
            elif self.trust_env:
                # No explicit or .env proxies, but allow HTTPX to read real OS env (incl. NO_PROXY)
                client_options = dict(self._client_kwargs)
                client_options.pop("timeout", None)
                self.session = httpx.Client(timeout=timeout, trust_env=True, **client_options)
            else:
                # Hard-disable env proxies
                client_options = dict(self._client_kwargs)
                client_options.pop("timeout", None)
                self.session = httpx.Client(timeout=timeout, trust_env=False, **client_options)

    def _log(self, message: str):
        """
        Internal logging helper. Logs message if logging is enabled.
        """
        if self.logger:
            self.logger.info(message)


    def _collect_proxy_config(self) -> tuple[Optional[str], Optional[Dict[str, httpx.HTTPTransport]]]:
        """
        Resolve proxy configuration according to HTTPX docs and project env rules:
        - Prefer explicit `mounts` (handled by __init__).
        - Else prefer explicit `proxy` (handled by __init__).
        - Else consult one env source:
            * If self.env_config is a non-empty dict (load_env_vars=True), use it.
            * Else if self.trust_env is True, use real os.environ.
            * Else, do not resolve from env.

        Returns:
            (proxy, mounts): One of these may be non-None if a proxy config was found.
        """
        # Choose a single environment source
        source_env: Optional[Dict[str, str]] = None
        if isinstance(self.env_config, dict) and len(self.env_config) > 0:
            source_env = {k: v for k, v in self.env_config.items() if isinstance(k, str) and isinstance(v, str)}
        elif self.trust_env:
            source_env = dict(os.environ)
        else:
            return None, None

        def _get(key: str) -> Optional[str]:
            return source_env.get(key) or source_env.get(key.lower())

        all_proxy = _get("ALL_PROXY")
        http_proxy = _get("HTTP_PROXY")
        https_proxy = _get("HTTPS_PROXY")

        # If both schemes are provided and differ, build per-scheme mounts
        if http_proxy and https_proxy and http_proxy != https_proxy:
            return None, {
                "http://": httpx.HTTPTransport(proxy=http_proxy),
                "https://": httpx.HTTPTransport(proxy=https_proxy),
            }

        # If ALL_PROXY is set (or single scheme available), use a single proxy
        single = all_proxy or https_proxy or http_proxy
        if single:
            return single, None

        # No proxy info available in the chosen env source
        return None, None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        auth: Optional[Union[tuple, Auth]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_kwargs: Optional[Dict[str, Any]] = None,
        **request_kwargs,
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
            **request_kwargs: Any additional options forwarded to `httpx.Client.request` (e.g., `verify`, `timeout`, `follow_redirects`).

            Note: Proxies are applied at client construction via `proxy` or per-scheme `mounts`, and `trust_env`.
            To change them, re‑instantiate the connector.

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
                **request_kwargs,
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
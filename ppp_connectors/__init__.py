# API connectors
import warnings

warnings.warn(
    (
        "The 'ppp_connectors' package is deprecated and no longer maintained. "
        "Please migrate to the 'apiary' package. "
        "See https://github.com/robd518/apiary for details."
    ),
    DeprecationWarning,
    stacklevel=2,
)

from ppp_connectors.api_connectors import (
    urlscan,
    spycloud,
    twilio,
    flashpoint,
    ipqs,
    generic,
)

# DBMS connectors
from ppp_connectors.dbms_connectors import (
    elasticsearch,
    mongo,
    odbc,
    splunk
)

# Export the modules and re-exports
__all__ = [
    "elasticsearch",
    "flashpoint",
    "generic",
    "ipqs",
    "mongo",
    "odbc",
    "splunk",
    "spycloud",
    "twilio",
    "urlscan",
]
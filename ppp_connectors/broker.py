"""
Shim for backward compatibility.
Forwards to ppp_connectors.connectors.broker.
TODO: Deprecate this file in a future major release.
"""

import warnings
from ppp_connectors.connectors.broker import *

warnings.warn(
    "ppp_connectors.broker is deprecated and will be removed in a future release; use ppp_connectors.connectors.broker instead.",
    DeprecationWarning,
    stacklevel=2
)
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Optional, TypedDict
import json
import math
import uuid

from version import VERSION

# Posterior mean difference below this threshold indicates insufficient separation
MIN_SEPARATION = 0.05

"""Package-level configurations"""

import os


DEBUG = bool(os.environ.get("DEBUG", False))

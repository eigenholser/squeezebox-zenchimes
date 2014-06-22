#!/usr/bin/env python
import os
import sys

APP_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    os.environ.setdefault("SETTINGS_MODULE", "zenchimes.settings")
    os.environ.setdefault("APP_ROOT", APP_ROOT)
    from zenchimes.server import main
    main()

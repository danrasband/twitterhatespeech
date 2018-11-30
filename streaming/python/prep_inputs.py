#!/usr/bin/env python3

import sys
import re

for line in sys.stdin:
    line_clean = re.sub("[^a-zA-Z0-9]+", "", line.lower())
    print(f"{line_clean.strip()}")

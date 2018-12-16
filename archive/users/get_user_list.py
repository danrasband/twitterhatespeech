#!/usr/bin/env python3.6

import sys

for line in sys.stdin:
    record = line.split('\t')
    print(record[3])

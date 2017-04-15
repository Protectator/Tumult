#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of Tumult.
"""
from argparse import ArgumentParser
import server


# Argument parsing
parser = ArgumentParser(
    description="shows statistics about Discord servers.")
parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
args = parser.parse_args()

server.run()
import requests
import os
from JellyFin import Client
import logging

import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Example argument parser')

# Add arguments to the parser
parser.add_argument('-u', '--userid', required=True, help='Input UserID')
# parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction, default=False, help='Enable verbose mode')

# Parse the command-line arguments
args = parser.parse_args()

client = Client.JellyfinClient()

client.set_user(args.userid)

client.move_items()
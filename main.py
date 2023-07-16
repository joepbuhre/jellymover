import requests
import os
from JellyFin import Client
import logging

import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Jellymover. Automatically archive seen episodes / movies')

# Add arguments to the parser
parser.add_argument('-u', '--userid',nargs='+', default=None, help='Input UserID')
parser.add_argument('-a', '--apikey', default=None, help='Put in Jellyfin api key')
parser.add_argument('-s', '--serverurl', default=None, help='Put in the Jellyfin server url')
parser.add_argument('-f', '--from-replace', default="", help="If you need to replace, specify from Path")
parser.add_argument('-t', '--to-replace', default="", help="If you need to replace, specify to path")
parser.add_argument('-d', '--dry-run', action=argparse.BooleanOptionalAction, default=False, help="Enable Dry run mode (don't actually move)")
parser.add_argument('-p', '--archive-path', default=None, help="Specify path which it needs to be archived to")
parser.add_argument('-l', '--log-level', default='INFO', help='Put in the logging level')
parser.add_argument('--reset', action=argparse.BooleanOptionalAction, default=False, help="Reset all items of the Archive tag")

# Parse the command-line arguments
try:
    args = parser.parse_args()

    client = Client.JellyfinClient(
        SERVER_URL=args.serverurl,
        API_KEY=args.apikey,
        FROM_REPLACE=args.from_replace,
        TO_REPLACE=args.to_replace,
        ARCHIVE_PATH=args.archive_path,
        DRY_RUN=args.dry_run,
        LOG_LEVEL=args.log_level
    )

    if args.userid == None:
        client.log.critical("Userid has not been set!")

    for userid in args.userid:
        client.set_user(userid)

        if args.archive_path != None:
            client.move_items()
        elif args.archive_path == None and args.reset == True:
            client.reset()
        else:
            parser.print_help()

except KeyboardInterrupt as e:
    client.log.critical("Run has been cancelled by user")
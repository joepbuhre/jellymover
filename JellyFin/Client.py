from argparse import Namespace
import logging
import os
import re
from dotenv import load_dotenv
from requests import Response, request
from JellyFin.Types import ErrorResponse
from .Log import get_logger
import json 

class Globals:
    ENV_PREFIX='JWM'

class JellyfinClient:
    
    def __init__(self, SERVER_URL = None, API_KEY = None, FROM_REPLACE = "", TO_REPLACE = "", ARCHIVE_PATH = None, DRY_RUN = None, LOG_LEVEL = logging.INFO, args: Namespace = None):
        # Load Dotenv 
        load_dotenv()

        SERVER_URL = self.__getenv('SERVER_URL', SERVER_URL)
        API_KEY = self.__getenv('API_KEY', API_KEY)
        FROM_REPLACE = self.__getenv('FROM_REPLACE', FROM_REPLACE)
        TO_REPLACE = self.__getenv('TO_REPLACE', TO_REPLACE)
        ARCHIVE_PATH = self.__getenv('ARCHIVE_PATH', ARCHIVE_PATH)

        self.log = get_logger(LOG_LEVEL)
        
        self.log.info('Started jellymover')

        if SERVER_URL == None: self.log.critical('SERVER_URL variable not found')
        if API_KEY == None: self.log.critical('API_KEY variable not found')
        if FROM_REPLACE == None: self.log.warning('FROM_REPLACE variable not found')
        if TO_REPLACE == None: self.log.warning('TO_REPLACE variable not found')
        if ARCHIVE_PATH == None and args.reset == False: self.log.critical('ARCHIVE_PATH variable not found')

        self.SERVER_URL = SERVER_URL
        self.API_KEY = API_KEY
        self.FROM_REPLACE = FROM_REPLACE
        self.TO_REPLACE = TO_REPLACE
        self.ARCHIVE_PATH = ARCHIVE_PATH
        self.DRY_RUN = bool(self.__getenv('DRY_RUN', DRY_RUN))
        self.args = args
        self.__handle_filter(args)

    
    def __getenv(self, var, primary):
        if primary != None:
            return primary
        else:
            return os.getenv(f"{Globals.ENV_PREFIX}_{var}", None)

    def __handle_filter(self, arg: Namespace):
        exclude_list = set()
        include_list = set()
        
        # Set excludes
        if arg.exclude != None:
            exclude_list.update(arg.exclude)
        
        if arg.exclude_file != None:
            with open(arg.exclude_file, 'rt') as f:
                exclude_file_list = list(filter(lambda l: l != "", f.read().splitlines()))
                exclude_list.update(exclude_file_list)
                
        # Set includes
        if arg.include != None:
            include_list.update(arg.include)
        
        if arg.include_file != None:
            with open(arg.include_file, 'rt') as f:
                include_file_list = list(filter(lambda l: l != "", f.read().splitlines()))
                include_list.update(include_file_list)
        
        self.exclude_list = exclude_list
        self.include_list = include_list
    
    def __regmatch_list(self, regex: list, values: list):
        for reg in regex:
            for value in values:
                if re.match(reg, value, re.IGNORECASE):
                    return True
        return False

    def get_user(self):
        """
        Sometimes you set the userid in env variables this is the way to fetch them
        """
        return self.__getenv('userid', None)

    def set_user(self, userid: str):
        """
        For a lot of Jellyfin endpoint we need to set the user id to get the items. Specifically for getting watched items.
        However, we can change this one if that's necessary
        """
        userid = self.__getenv('USERID', userid)
        if userid == None: self.log.critical('Userid variable not found')

        # Check if user exists
        try:
            res = self.__api('GET', f'/Users/{userid}')
        except ConnectionError as e:
            # e: {'message': str, 'response': Response} = e.args[0]
            err: ErrorResponse = e.args[0]
            resp = err['response']
            if resp.status_code == 400:
                self.log.critical('Bad request: %s', resp.text)
            elif resp.status_code == 404:
                self.log.critical('User not found: %s', resp.text)
            elif resp.status_code == 401:
                self.log.critical(err['message'])
            else:
                self.log.critical('Unkown error has occured %s', resp.text)   


        if res.status_code > 299:
            print('hi')
            self.log.error('User has not been found, please check. Response: %s',res.text )
        
        self.userid = userid

    def __api(self, method, path, params = {}, **kwargs) -> Response:
        """
        API wrapper
        """
        url = f"{self.SERVER_URL}{path}"
        headers = {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': f'MediaBrowser Token="{self.API_KEY}"'
        }

        res = request(method, url, headers=headers, params=params, **kwargs)

        if res.status_code > 299:
            raise ConnectionError({
                'message': f'Error with status code [{res.status_code}]',
                'response': res
            })
        else:
            return res

    def get_item(self, id: str):
        res = self.__api('GET', f'/Users/{self.userid}/Items/{id}')
        return res.json()

    def update_item(self, obj):
        res = self.__api('POST', f'/Items/{obj["Id"]}', data=json.dumps(obj))
        return res

    def move_items(self):
        res = self.__api('GET', '/Items', {
            'userId': self.userid,
            'filters': 'IsPlayed',
            'recursive': 'true',
            'sortBy': 'DatePlayed',
            'fields': 'Tags,Path'
        })

        media = res.json()['Items']

        # Filter unneeded media
        def filter_media(m):
            # If archived, exit early
            if 'Archived' in m['Tags']:
                return False
            
            lst = [m['Name']]
            if 'SeriesName' in m: lst.append(m['SeriesName'])

            exclude_result = True if len(self.exclude_list) == 0 else self.__regmatch_list(self.exclude_list, lst) == False
            include_result = True if len(self.include_list ) == 0 else self.__regmatch_list(self.include_list, lst) == True

            return (exclude_result and include_result)

        original_length = len(media)
        media = list(
            filter(filter_media, media)
        )
        
        # Set checked count so we know when to stop
        self.log.info(f'Loaded & filtered items, {len(media)} items can be moved')
        for (i, item) in enumerate(media):

            # Display series name if running
            seriesname = f"series [{item['SeriesName']}], " if 'SeriesName' in item else ''
            self.log.info(f'Moving {seriesname}item [{item["Name"]}] ({i + 1} of {len(media)})')

            src_path = str(item['Path']).replace(self.FROM_REPLACE, self.TO_REPLACE)
            
            path, file = os.path.split(src_path)

            to_move = os.path.splitext(file)[0]

            # Rsync command
            rsync_cmd = f"rsync --progress --remove-source-files -a --relative --include='*/' --include='*{to_move}*' --exclude='*' '{path}' {self.ARCHIVE_PATH}"
            self.log.debug(rsync_cmd)

                # Run only when dry run is false
            if self.DRY_RUN == False:
                if os.path.exists(src_path):
                    os.system(rsync_cmd)

                # We're done, adding the Tag archived :D. Getting the full item otherwise JF will overwrite or forget fields.
                full_item = self.get_item(item['Id'])
                full_item['Tags'].append('Archived')
                self.update_item(full_item)
            else:
                self.log.debug('Dry run enabled, skipping...')
            
            if self.args.limit != 0 and (i + 1) >= self.args.limit:
                break

        self.log.info(f'All done. [Moved {i + 1} items] [Checked {original_length} items]')

    def reset(self):
        res = self.__api('GET', '/Items', {
            'userId': self.userid,
            'recursive': 'true',
            'tags': 'Archived'
        })

        media = res.json()['Items']

        self.log.info(f'Unarchiving {len(media)} item(s)')

        for (i, obj) in enumerate(media):

            item = self.get_item(obj['Id'])
            self.log.debug(f'Currently resetting item [{obj["Name"]}], [{item["Id"]}]')

            if 'Archived' in item['Tags']:
                item['Tags'].remove('Archived')
                self.update_item(item)
        
        self.log.info('Unarchiving done')
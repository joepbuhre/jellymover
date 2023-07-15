import os
#import Globals
from dotenv import load_dotenv
from requests import Response, request
from .Log import get_logger
import json 

class Globals:
    ENV_PREFIX='JWM'

class JellyfinClient:
    
    def __init__(self, SERVER_URL = None, API_KEY = None, FROM_REPLACE = None, TO_REPLACE = None, ARCHIVE_PATH = None, DRY_RUN = None):
        # Load Dotenv 
        load_dotenv()

        SERVER_URL = self.__getenv('SERVER_URL', SERVER_URL)
        API_KEY = self.__getenv('API_KEY', API_KEY)
        FROM_REPLACE = self.__getenv('FROM_REPLACE', FROM_REPLACE)
        TO_REPLACE = self.__getenv('TO_REPLACE', TO_REPLACE)
        ARCHIVE_PATH = self.__getenv('ARCHIVE_PATH', ARCHIVE_PATH)

        self.log = get_logger()
        
        self.log.info('Started jellymover')

        if SERVER_URL == None: self.log.error('SERVER_URL variable not found'); exit()
        if API_KEY == None: self.log.error('API_KEY variable not found'); exit()
        if FROM_REPLACE == None: self.log.error('FROM_REPLACE variable not found'); exit()
        if TO_REPLACE == None: self.log.error('TO_REPLACE variable not found'); exit()
        if ARCHIVE_PATH == None: self.log.error('ARCHIVE_PATH variable not found'); exit()

        self.SERVER_URL = SERVER_URL
        self.API_KEY = API_KEY
        self.FROM_REPLACE = FROM_REPLACE
        self.TO_REPLACE = TO_REPLACE
        self.ARCHIVE_PATH = ARCHIVE_PATH
        self.DRY_RUN = bool(self.__getenv('DRY_RUN', False))
    
    def __getenv(self, var, alternate):
        return os.getenv(f"{Globals.ENV_PREFIX}_{var}", alternate)

    
    def set_user(self, userid: str):
        """
        For a lot of Jellyfin endpoint we need to set the user id to get the items. Specifically for getting watched items.
        However, we can change this one if that's necessary
        """
        if self.__getenv('USERID', userid) == None: self.log.error('Userid variable not found'); exit()
        self.userid = self.__getenv('USERID', userid)

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
            raise ConnectionError(f'Error with status code [{res.status_code}]')
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
        })

        media = res.json()['Items']
        
        for (i, obj) in enumerate(media):

            item = self.get_item(obj['Id'])

            if 'Archived' not in item['Tags']: 
                
                self.log.info(f'Currently at item [{obj["Name"]}], [{item["Id"]}]')

                src_path = str(item['Path']).replace(self.FROM_REPLACE, self.TO_REPLACE)
                
                # self.log.debug(item['Path'])

                path, file = os.path.split(src_path)

                to_move = os.path.join(path, os.path.splitext(file)[0])

                # self.log.debug(to_move)

                # Rsync command
                rsync_cmd = f"rsync --progress --remove-source-files -a --relative --include '{to_move}*' '{path}' {self.ARCHIVE_PATH}"
                self.log.debug(rsync_cmd)

                if os.path.exists(src_path):
                    # Run only when dry run is false
                    if self.DRY_RUN == False:
                        os.system(rsync_cmd)

                        # We're done, adding the Tag archived :D
                        item['Tags'].append('Archived')
                        self.update_item(item)

    def reset(self):
        res = self.__api('GET', '/Items', {
            'userId': self.userid,
            'recursive': 'true',
            'tags': 'Archived'
        })

        # media = filter(lambda obj: obj['Type'] == 'Movie', res.json()['Items'])
        media = res.json()['Items']

        self.log.info(f'Unarchiving {len(media)} item(s)')

        for (i, obj) in enumerate(media):

            item = self.get_item(obj['Id'])
            self.log.debug(f'Currently resetting item [{obj["Name"]}], [{item["Id"]}]')

            if 'Archived' in item['Tags']:
                item['Tags'].remove('Archived')
                self.update_item(item)
        
        self.log.info('Unarchiving done')
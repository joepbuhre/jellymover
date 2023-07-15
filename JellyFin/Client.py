import os
#import Globals
from dotenv import load_dotenv
from requests import Response, request
from .Log import get_logger
import json 

class Globals:
    ENV_PREFIX='JWM'

class JellyfinClient:
    
    def __init__(self, SERVER_URL = None, API_KEY = None, FROM_REPLACE = None, TO_REPLACE = None, ARCHIVE_PATH = None):
        # Load Dotenv 
        load_dotenv()

        SERVER_URL = self.__getenv('SERVER_URL', SERVER_URL)
        API_KEY = self.__getenv('API_KEY', API_KEY)
        FROM_REPLACE = self.__getenv('FROM_REPLACE', FROM_REPLACE)
        TO_REPLACE = self.__getenv('TO_REPLACE', TO_REPLACE)
        ARCHIVE_PATH = self.__getenv('ARCHIVE_PATH', ARCHIVE_PATH)

        self.log = get_logger()

        self.log.info('test')

        if SERVER_URL == None: raise NameError('SERVER_URL variable not found')
        if API_KEY == None: raise NameError('API_KEY variable not found')
        if FROM_REPLACE == None: raise NameError('FROM_REPLACE variable not found')
        if TO_REPLACE == None: raise NameError('TO_REPLACE variable not found')
        if ARCHIVE_PATH == None: raise NameError('ARCHIVE_PATH variable not found')

        self.SERVER_URL = SERVER_URL
        self.API_KEY = API_KEY
        self.FROM_REPLACE = FROM_REPLACE
        self.TO_REPLACE = TO_REPLACE
        self.ARCHIVE_PATH = ARCHIVE_PATH
    
    def __getenv(self, var, alternate):
        return os.getenv(f"{Globals.ENV_PREFIX}_{var}", alternate)

    
    def set_user(self, userid: str):
        """
        For a lot of Jellyfin endpoint we need to set the user id to get the items. Specifically for getting watched items
        """
        self.userid = userid

    def __api(self, method, path, params = {}, **kwargs) -> Response:
        """
        API wrapper
        """
        # url = "https://jf.vicinusvetus.nl/Items?userId=d9871f7d73ff45e797770cf6436c397b&filters=IsPlayed&recursive=true&sortBy=DatePlayed"
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

    def get_played(self):
        res = self.__api('GET', '/Items', {
            'userId': self.userid,
            'filters': 'IsPlayed',
            'recursive': 'true',
            'sortBy': 'DatePlayed',
            'nameStartsWith': 'Ghosted'
        })

        movies = filter(lambda obj: obj['Type'] == 'Movie', res.json()['Items'])
        
        for (i, obj) in enumerate(movies):

            item = self.get_item(obj['Id'])
            
            self.log.debug(f'Currently at item [{obj["Name"]}], [{item["Id"]}]')

            src_path = str(item['Path']).replace('/media', '/srv/ssd1/.')
            
            self.log.debug(item['Path'])

            path, file = os.path.split(src_path)

            to_move = os.path.join(path, os.path.splitext(file)[0])

            self.log.debug(to_move)

            # Rsync command
            rsync_cmd = f"rsync --progress --remove-source-files -a --relative --include '{to_move}*' '{path}' /srv/hdd1"

            if os.path.exists(src_path):
                self.log.debug("Path found, moving now")
                self.log.info(rsync_cmd)

                # Run only when dry run is false
                if bool(self.__getenv('DRY_RUN', False)) == False:
                    os.system(rsync_cmd)

            if 'Archived' not in item['Tags']: 
                item['Tags'].append('Archived')
                self.update_item(item)
            else:
                self.log.debug('Already archived')






# payload = {}

# response = requests.request("GET", url, headers=headers, data=payload)

# data = response.json()['Items']

# movies = filter(lambda obj: obj['Type'] == 'Movie', data)

# for (i, obj) in enumerate(movies):
#     print(f'Currently at item [{obj["Name"]}]')



    # url = f"https://jf.vicinusvetus.nl/Users/d9871f7d73ff45e797770cf6436c397b/Items/{obj['Id']}"

    # req2 = requests.request("GET", url, headers=headers)


    # print(req2.json()['Path'])
    # print("")

    # print(os.path.exists(req2.json()['Path']))
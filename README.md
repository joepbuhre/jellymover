# Jellymover - Automatically Archive Seen Episodes/Movies

Jellymover is a command-line Python application that enables the automatic archiving of seen episodes/movies in a Jellyfin media server.

## Usage

```shell
python jellymover.py [options]
```

## Docker Usage
This application is also available with docker. This is also the preference. 
### Examples

1. Plain run with docker. (use -it for keyboard interrupt)
    ```bash
    docker run --rm -it -v /srv:/srv ghcr.io/joepbuhre/jellymover [options]
    ```
2. Create alias in source ~/.bashrc
    ```bash
    alias jellymover=docker run --rm -it -v /srv:/srv ghcr.io/joepbuhre/jellymover

    # Usage
    jellymover -u <userid>

    ```
> Don't forget when using docker using correct volumes otherwise it will not detect the path and assumes it's already archived!


## Command-Line Options

| Option         | Description                                               |
| -------------- | --------------------------------------------------------- |
| `-u`, `--userid` | Input UserID                                             |
| `-a`, `--apikey` | Set Jellyfin API key                                     |
| `-s`, `--serverurl` | Set the Jellyfin server URL                             |
| `-f`, `--from-replace` | Specify the "from" path for replacement                |
| `-t`, `--to-replace` | Specify the "to" path for replacement                    |
| `-d`, `--dry-run` | Enable dry run mode (do not actually move items)         |
| `-p`, `--archive-path` | Specify the path to which items should be archived     |
| `-l`, `--log-level` | Set the logging level                                    |
| `--reset` | Reset all items of the Archive tag                        |

## Examples

1. Archive seen episodes/movies for a specific user:

   ```shell
   python jellymover.py -u <userid> -a <apikey> -s <serverurl> -p <archive-path>
   ```

2. Perform a dry run to simulate the archiving process:

   ```shell
   python jellymover.py -u <userid> -a <apikey> -s <serverurl> -p <archive-path> -d
   ```

3. Reset all items of the Archive tag for a user:

   ```shell
   python jellymover.py -u <userid> -a <apikey> -s <serverurl> --reset
   ```
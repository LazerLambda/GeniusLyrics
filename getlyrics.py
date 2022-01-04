"""Get Lyrics Script.

Script to retrieve lyrics from genius api
based on a list of artists.
"""

import argparse
import datetime
import json
import os
import re
import urllib3

from lyricsgenius import Genius
from dotenv import load_dotenv, find_dotenv

ERROR: str = "ERROR:\n\t'-> %s is None"


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    client_access_token: str = os.environ.get(
        "GENIUS_CLIENT_ACCESS_TOKEN", None)
    assert client_access_token is not None,\
        ERROR % "GENIUS_CLIENT_ACCESS_TOKEN"

    description: str = (
        'Get lyrics from genius API.',
        'Provide file with artists on each',
        'line and define the maximum of songs to retrieve.')
    parser: any = argparse.ArgumentParser(
        description=description)
    parser.add_argument(
        '--artists',
        dest='artists',
        type=str,
        required=True,
        default=None,
        help='Plain file including artists (on each line) to get lyrics from.')
    parser.add_argument(
        '--max',
        dest='max_n',
        type=int,
        default=1000,
        help='Max songs for each artist.')
    args: dict = parser.parse_args()

    file_path: str = args.artists
    max_n: int = args.max_n

    if not os.path.isfile(file_path):
        raise FileNotFoundError()

    artists: list = list()
    with open(file_path, 'r') as file:
        while (artist := file.readline().rstrip()):
            artists.append(artist)

    data: dict = dict()
    interrupted: list = list()

    for artist in artists:
        api: any = Genius(client_access_token)

        # Catch Interruptions
        try:
            artist: any = api.search_artist(
                artist,
                max_songs=max_n,
                include_features=True)
            lyrics: list = [song.lyrics for song in artist.songs]

            # filter for artifacts
            filter_lyrics: list = list(
                map(lambda lyric: re.sub(
                        r'(EmbedShare URLCopyEmbedCopy)',
                        '',
                        lyric),
                    lyrics))

            data[str(artist)] = filter_lyrics
        except urllib3.exceptions.HTTPError:
            interrupted.append(artist)

    data["interrupted"] = interrupted
    filename: str = 'lyrics_' +\
        str(len(artists)) +\
        '_' +\
        str(datetime.datetime.now()) +\
        '.json'
    with open(filename, 'w') as fout:
        json_dumps_str = json.dumps(data, indent=4)
        print(json_dumps_str, file=fout)

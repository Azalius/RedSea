#!/usr/bin/env python

import redsea.cli as cli
from redsea.mediadownloader import MediaDownloader
from redsea.tagger import Tagger
from redsea.tidal_api import TidalApi, TidalError
from redsea.sessions import SimpleSessionFile

from config.settings import PRESETS
import os


LOGO = """
 /$$$$$$$                  /$$  /$$$$$$                     
| $$__  $$                | $$ /$$__  $$                    
| $$  \ $$  /$$$$$$   /$$$$$$$| $$  \__/  /$$$$$$   /$$$$$$ 
| $$$$$$$/ /$$__  $$ /$$__  $$|  $$$$$$  /$$__  $$ |____  $$
| $$__  $$| $$$$$$$$| $$  | $$ \____  $$| $$$$$$$$  /$$$$$$$
| $$  \ $$| $$_____/| $$  | $$ /$$  \ $$| $$_____/ /$$__  $$
| $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$/|  $$$$$$$|  $$$$$$$
|__/  |__/ \_______/ \_______/ \______/  \_______/ \_______/

                    (c) 2016 Joe Thatcher
               https://github.com/Azalius/RedSea
\n"""

MEDIA_TYPES = {'t': 'track', 'p': 'playlist', 'a': 'album', 'f': 'album', 'artist': 'artist'}


def main():
    # Get args
    args = cli.get_args()

    # Check for auth flag / session settings
    currentSession = SimpleSessionFile('./config/sessions.pk')
    deal_with_auth(currentSession, args)

    print(LOGO)

    # Load config
    try:
        preset = PRESETS[args.preset]
    except KeyError :
        print("Unknown preset : "+args.preset)
        exit(2)

    # Parse options
    preset['quality'] = []
    preset['quality'].append('HI_RES') if preset['MQA_FLAC_24'] else None
    preset['quality'].append('LOSSLESS') if preset['FLAC_16'] else None
    preset['quality'].append('HIGH') if preset['AAC_320'] else None
    preset['quality'].append('LOW') if preset['AAC_96'] else None

    media_to_download = cli.parse_media_option(args.urls)

    # Loop through media and download if possible
    cm = 0
    for mt in media_to_download:
        # Is it an acceptable media type? (skip if not)
        if not mt['type'] in MEDIA_TYPES:
            print('Unknown media type - ' + mt['type'])
            continue

        cm += 1
        print('<<< Getting {0} info... >>>'.format(MEDIA_TYPES[mt['type']]), end='\r')
        
        # Create a new TidalApi and pass it to a new MediaDownloader
        mediaDownloader = MediaDownloader(TidalApi(currentSession.load_session()), preset, Tagger(preset))

        # Get media info
        try:
            tracks, media_info = get_tracks(mt, mediaDownloader)
        except StopIteration:
            # Let the user know we cannot download this release and skip it
            print('The account is not able to get info for release {}. Skipping..'.format(mt['id']))
            continue

        total = len(tracks)

        # Single
        if total == 1:
            print('<<< Downloading single track... >>>')

        # Playlist or album or artist
        else:
            print('<<< Downloading {0}: {1} track(s) in total >>>'.format(
                MEDIA_TYPES[mt['type']], total))

        cur = 0
        for track in tracks:
            # Actually download the track (finally)
            while True:
                try:
                    mediaDownloader.download_media(track, preset['quality'], args.outdir, media_info)
                    break

                # Catch quality error
                except ValueError as e:
                    print("\t" + str(e))
                    if args.skip is True:
                        print('Skipping track "{} - {}" due to insufficient quality'.format(
                            track['artist']['name'], track['title']))
                        break
                    else:
                        print('Halting on track "{} - {}" due to insufficient quality'.format(
                            track['artist']['name'], track['title']))
                        quit()

                # Catch session audio stream privilege error
                except AssertionError as e:
                    if args.skip is True:
                        print(str(e) + '. Skipping...')
                        break
                    else:
                        print(str(e) + '. Stopping. Use -s to skip instead')
                        quit()

            # Progress of current track
            cur += 1
            print('=== {0}/{1} complete ({2:.0f}% done) ===\n'.format(
                cur, total, (cur / total) * 100))
        
        # Progress of queue
        print('> Download queue: {0}/{1} items complete ({2:.0f}% done) <\n'.
            format(cm, len(media_to_download),
                    (cm / len(media_to_download)) * 100))

    print('> All downloads completed. <')


def deal_with_auth(RSF, args):
    if args.identifiant is None and args.password is None: pass
    elif args.identifiant is not None and args.password is None:
        print("You need to specify a password with an ID")
    elif args.identifiant is None and args.password is not None:
        print("You need to specify a password with an ID")
    else:
        try:
            RSF.new_session("default", args.identifiant, args.password)
        except Exception as e:
            print("Impossible to log-in : " + str(e))
            exit()
    try:
        RSF.load_session()
    except Exception as e:
        print("Authentication impossible : "+str(e))
        exit()


def get_tracks(media, md):
    tracks = []
    media_info = None

    while True:
        try:
            # Track
            if media['type'] == 't':
                tracks.append(md.api.get_track(media['id']))

            # Playlist
            elif media['type'] == 'p':

                # Make sure only tracks are in playlist items
                playlistItems = md.api.get_playlist_items(media['id'])['items']
                for item in playlistItems:
                    if item['type'] == 'track':
                        tracks.append(item['item'])

            elif media['type'] == 'artist':
                tracks = md.api.get_artist_tracks(media['id'])['items']

            # Album
            else:
                # Get album information
                media_info = md.api.get_album(media['id'])

                # Get a list of the tracks from the album
                tracks = md.api.get_album_tracks(media['id'])['items']

            return tracks, media_info
        except TidalError as e:
                raise(e)


# Run from CLI - catch Ctrl-C and handle it gracefully
if __name__ == '__main__':
    oldpath = str(os.path.curdir)
    os.chdir(os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))) # so other path can be taken relatively
    try:
        main()
    except KeyboardInterrupt:
        print('\n^C pressed - abort')
    else:
        print("Download over")
    finally:
        print("Exiting...")
        os.chdir(oldpath)
        exit()

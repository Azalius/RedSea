import argparse
import re
from urllib.parse import urlparse


def get_args():
    #
    # argparse setup
    #
    parser = argparse.ArgumentParser(
        description='A music downloader for Tidal.')

    parser.add_argument(
        '-p',
        '--preset',
        default='default',
        help='Select a download preset. Defaults to Lossless only. See /config/settings.py for presets')

    parser.add_argument(
        '-id',
        '--identifiant',
        default=None,
        help='Specifies the Tidal ID. Needs to be passed only the first time, with a password.')

    parser.add_argument(
        '-pwd',
        '--password',
        default=None,
        help='Specifies the Tidal password. Needs to be passed only the first time, with an ID.')

    parser.add_argument(
        '-o',
        '--outdir',
        default='.',
        help='Specifies the output directory. Might need to wrap it in quotes')

    parser.add_argument(
        '-s',
        '--skip',
        action='store_true',
        default=False,
        help='Pass this flag to skip track and continue when a track does not meet the requested quality')

    parser.add_argument(
        'urls',
        nargs='+',
        help=
        'The URLs to download. You may need to wrap the URLs in double quotes if you have issues downloading.'
    )

    return parser.parse_args()


def parse_media_option(urls):
    opts = []
    for url in urls:
        if is_valid_url(url):
            url = re.sub(r'tidal.com\/.{2}\/store\/', 'tidal.com/', url)
            url = re.sub(r'tidal.com\/store\/', 'tidal.com/', url)
            url = urlparse(url)
            components = url.path.split('/')
            if not components or len(components) <= 2:
                print('Invalid URL: ' + url)
                exit()
            type_ = components[1]
            id_ = components[2]
            if type_ == 'album':
                type_ = 'a'
            elif type_ == 'track':
                type_ = 't'
            elif type_ == 'playlist':
                type_ = 'p'
            elif type_ == 'artist':
                type_ = 'artist'
            opts.append({'type': type_, 'id': id_})
            continue
        elif ':' in url and '#' in url:
            ci = url.index(':')
            hi = url.find('#')
            hi = len(url) if hi == -1 else hi
            o = {'type': url[:ci], 'id': url[ci + 1:hi], 'index': url[hi + 1:]}
            opts.append(o)
        else:
            print('Input "{}" does not appear to be a valid url.'.format(url))
    return opts


def is_valid_url(url):
    return url.startswith('http')

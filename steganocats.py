#!/usr/bin/env python3

# Standard Lib
import argparse
import json
from os import path, listdir
import random

# PIP modules
import flickrapi
import requests

# Steganocats modules
from MemeWriter import MemeWriter

# Global Constants
SECRETS_FILE = 'secrets.json'
IMAGES_DIR = 'base_images'
SAVE_DIR = 'memes'
PHRASE_FILE = 'hazburger.txt'


# Parse command-line arguments
parser = argparse.ArgumentParser('Make some STEGANOCATS')
parser.add_argument('-t', '--tag', dest='tag', action='store', default='cat',
                    help='flickr search tag', metavar='flickr tag')
parser.add_argument('--meme', dest='meme_only', action='store_true',
                    default=False, help='make meme only, no steganograghy')
parser.add_argument('--steg', dest='steg_only', action='store_true',
                    default=False, help='make steganograghy only, no meme')
parser.add_argument('-m', '--mode', dest='mode', default='RGBA',
                    action='store', help='mode to process image in',
                    choices={'L', 'RGBA'}, metavar='mode')
parser.add_argument('-b', '--base', dest='base_image', default=None,
                    help='base image to meme, steg, or search')
parser.add_argument('-f', '--flickr', dest='query_flickr', action='store_true',
                    default=False, help='query Flickr for images')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    default=False, help='show verbose comments')
parser.add_argument('-i', dest='infile', action='store',
                    help='file to be hidden in image', metavar='in file')
parser.add_argument('-S', dest='stego_bytes', action='store',
                    help='string to be hidden in image (as bytes)',
                    metavar='stego bytes', default='KITTYKATZ')
parser.add_argument('--search', dest='find_steg', action='store_true',
                    default=False, help='search base image')
args = parser.parse_args()


# Flickr functions (for getting images)
def get_secret(setting, json_obj):
    ''' Return secret value from loaded JSON file.'''
    try:
        return json_obj[setting]
    except KeyError:
        error_message = 'Unable to load {} variable.'.format(setting)
        raise AttributeError(error_message)


def make_flickr_api(secrets_filename, format='json'):
    ''' Return instance of FlickrAPI using credentials from secrets file.'''
    with open(secrets_filename) as f:
        secrets = json.loads(f.read())
    flickr_api_key = get_secret('flickr_api_key', secrets)
    flickr_api_secret = get_secret('flicker_api_secret', secrets)
    return flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret,
                               format=format)


def download_img(farm, server, photo_id, secret, owner, o_secret):
    ''' Given metadata from tag search JSON, attempt to DL image.'''
    file_path = path.relpath(IMAGES_DIR + '/' + photo_id + '_' + owner)
    if path.isfile(file_path) and args.verbose:
        print('Already have image.')
        return False
    url = 'https://farm{}.staticflickr.com/{}/{}_{}_b.jpg'.format(farm,
           server, photo_id, secret)
    if args.verbose:
        print('Using URL: \n %s' % url)
    r = requests.get(url)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(r.content)
            return True
    else:
        return False


def get_images_by_tag(flickr_api, tag='cat'):
    ''' Return a list of URLs to query for images.'''
    flickr = flickr_api
    resp = flickr.photos.search(tags=tag, license=[1, 2, 3, 5])
    resp = json.loads(str(resp, 'utf8'))
    for photo in resp['photos']['photo']:
        photo_id, secret, owner = photo['id'], photo['secret'], photo['owner']
        farm, server = photo['farm'], photo['server']
        # These lines useful for querying original, large-size images.
        # info = flickr.photos.getInfo(photo_id=photo_id, secret=secret)
        # info = json.loads(str(info, 'utf8'))
        # o_secret = info['photo']['originalsecret']
        if args.verbose:
            print('Attempting to download img: %s.' % photo_id)
        download_img(farm, server, photo_id, secret, owner, None)
    pass


# Get random file from IMAGES_DIR
def get_img_file(img_folder=IMAGES_DIR):
    ''' Return random image from specified folder.'''
    file_name = random.choice(listdir(img_folder))
    return file_name


# Draw meme text from default PHRASE_FILE
def get_meme_text():
    ''' Choose random phrase from PHRASE_FILE'''
    with open(PHRASE_FILE, 'r') as f:
        return random.choice(f.read().split('\n'))


def main():
    # Query flickr if flags set
    if args.query_flickr:
        flickr = make_flickr_api(SECRETS_FILE)
        get_images_by_tag(flickr, args.tag)
    # Instantiate meme writer
    meme_writer = MemeWriter(args.mode)

    # Allow for user selected image
    if not args.base_image:
        img_file = get_img_file()
    else:
        img_file = args.base_image
    if args.verbose:
        print('Using %s as base image.' % img_file)

    # if finding hidden message, do before anything else and pass
    if args.find_steg:
        if args.verbose:
            print('Searching for hidden bytes.')
        print(meme_writer.find_msg(img_file))
        return None

    if args.verbose:
        print('Doing meme steps.')
    # do meme making if not steganography only
    if not args.steg_only:
        meme_phrase = get_meme_text()
        img_obj = meme_writer.write_meme(path.join(IMAGES_DIR, img_file),
                                         meme_phrase)
        if args.meme_only:
            img_obj.save(path.join(SAVE_DIR, img_file + '-meme.png'))
            return None

    # finally do steganography if not meme only
    if args.verbose:
        print('Doing steganographic steps.')
    img = img_obj or path.join(IMAGES_DIR, img_file)
    if not args.infile:
        hidden = bytes(args.stego_bytes, 'utf8')
    else:
        hidden = open(args.infile, 'rb').read()
    meme_writer.hide_msg(img, hidden)
    img.save(path.join(SAVE_DIR, img_file + '-steg.png'))


if __name__ == '__main__':
    main()

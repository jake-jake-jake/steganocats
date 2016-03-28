#!/usr/bin/env python3

import json
from os import path, listdir
import requests
import random

import flickrapi

from MemeWriter import MemeWriter

SECRETS_FILE = 'secrets.json'
BASE_IMAGES_DIR = 'base_images'

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
    file_path = path.relpath(BASE_IMAGES_DIR + '/' + photo_id + '_' + owner)
    if path.isfile(file_path):
        print('Already have image.')
        return False
    url = 'https://farm{}.staticflickr.com/{}/{}_{}_b.jpg'.format(farm,
            server, photo_id, secret)
    print('Using URL: \n %s' % url)
    r =  requests.get(url)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(r.content)
            return True
    else:
        return False



def get_images_by_tag(tag='cat'):
    ''' Return a list of URLs to query for images.'''
    resp = flickr.photos.search(tags=tag, license=[1,2,3,5])
    resp = json.loads(str(resp, 'utf8'))
    for photo in resp['photos']['photo']:
        photo_id, secret, owner = photo['id'], photo['secret'], photo['owner']
        farm, server = photo['farm'], photo['server']
        info = flickr.photos.getInfo(photo_id=photo_id, secret=secret)
        info = json.loads(str(info, 'utf8'))
        o_secret = info['photo']['originalsecret']
        print('Attempting to download img: %s.' % photo_id)
        download_img(farm, server, photo_id, secret, owner, o_secret)
    pass


def get_img_file(img_folder=BASE_IMAGES_DIR):
    ''' Return random image from specified folder.'''
    file_name = random.choice(listdir(img_folder))
    return file_name


def get_meme_text(phrase_file='hazburger.txt'):
    ''' Choose random phrase from phrase_file'''
    with open(phrase_file, 'r') as f:
        return random.choice(f.read().split('\n'))


# flickr = make_flickr_api(SECRETS_FILE)
# get_images_by_tag('kitty')

def main(debug=True):
    if debug:
        for _ in range(10):
            img_folder = path.relpath(BASE_IMAGES_DIR)
            save_folder = path.relpath('memes/')
            msg = get_meme_text()
            print(msg)
            mode = random.choice(['L', 'RGBA'])
            print(mode)
            meme_writer = MemeWriter(mode)
            img = img_folder + '/' + get_img_file(img_folder)
            print(img)
            steganocat = meme_writer.write_meme(img, msg)
            meme_writer.hide_msg(steganocat, msg)
            steganocat.save(save_folder + '/' + str(_) + ".jpg")

if __name__ == '__main__':
    main()
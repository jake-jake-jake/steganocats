#!/usr/bin/env python3

import json
from os import path
import requests

import flickrapi

from MemeWriter import MemeWriter

SECRETS_FILE = 'secrets.json'


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
    url = 'https://farm{}.staticflickr.com/{}/{}_{}_o.jpg'.format(farm,
            server, photo_id, o_secret)
    print('Using URL: \n %s' % url)
    r =  requests.get(url)
    file_path = path.relpath('scraped_images/' + photo_id + '_' + owner)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(r.content)
            return True
    else:
        return False



def get_images_by_tag(tag='cat'):
    ''' Return a list of URLs to query for images.'''
    resp = flickr.photos.search(tags=tag, is_commons=True)
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


# flickr = make_flickr_api(SECRETS_FILE)
# get_images_by_tag('kitty')

def main(debug=False):
    if debug:
        msg = '''The Naming of Cats is a difficult matter,
        It isn't just one of your holiday games;
        You may think at first I'm as mad as a hatter
        When I tell you, a cat must have THREE DIFFERENT NAMES.'''
        meme_writer = MemeWriter()
        steganocat = meme_writer.write_meme('kitten.jpg', 'katz r kewl')
        meme_writer.hide_msg(steganocat, msg)
        steganocat.save('gks-stripes.jpg')
        print(meme_writer.find_msg(steganocat))

if __name__ == '__main__':
    main()
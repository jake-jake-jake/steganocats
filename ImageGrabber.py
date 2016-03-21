#!/usr/bin/env python3
import json


import flickrapi

SECRETS_FILE = 'secrets.json'

class ImageGrabber:
    ''' Class for  '''

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


    def get_image_urls(tag='cat'):
        ''' Return a list of URLs to query for images.'''
        resp = flickr.photos.search(tags=tag, is_commons=True)
        resp = json.loads(str(resp, 'utf8'))
        urls = []
        for photo in resp['photos']['photo']:
            photo_id, secret = photo['id'], photo['secret']
            info = flickr.photos.getInfo(photo_id=photo_id, secret=secret)
            info = json.loads(str(info, 'utf8'))
            urls.append(info['url'])
        return urls
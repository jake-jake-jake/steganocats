import json


import flickrapi
from PIL import Image, ImageDraw, ImageFont

SECRETS_FILE = 'steganocats.json'

# Flickr functions (for getting images)
def get_secret(setting, json_obj):
    ''' Return secret value from loaded JSON file.'''
    try:
        return json_obj[setting]
    except KeyError:
        error_message = 'Unable to load {} environment variable.'.format(setting)
        raise AttributeError(error_message)


def make_flickr_api(secrets_filename, format='json'):
    ''' Return instance of FlickrAPI using credentials from secrets file.'''
    with open(secrets_filename) as f:
        secrets = json.loads(f.read())
    flickr_api_key = get_secret('flickr_api_key', secrets)
    flickr_api_secret = get_secret('flicker_api_secret', secrets)
    return flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret, 
                               format=format)


def get_flickr_photos(FlickrAPI_obj, terms, is_commons=True):
    ''' Query instantiated FlickrAPI object for terms'''
    photo_json = FlickrAPI_obj.photos.search(terms)
    return photo_json


# PIL functions for processing image
def to_greyscale(image_filename):
    ''' Convert a full-color image into a greyscale image.'''
    gs = Image.open(image_filename).convert('L')
    return gs


def write_steg(image_obj, phrase):
    ''' Returns image with hazburger phrase superimposed on it.'''
    x, y = image_obj.size
    x_insert, y_insert = x // 2, 2 * y // 3
    size = y // 10
    font = ImageFont.truetype('impact.ttf', size=size)
    draw = ImageDraw.Draw(image_obj)
    draw.text((x_insert, y_insert), phrase, font=font, fill='white')
    return image_obj


flickr = make_flickr_api(SECRETS_FILE)

grey_kitty = to_greyscale('kitten.jpg')
grey_kitty_stegged = write_steg(grey_kitty, 'cheezburger')


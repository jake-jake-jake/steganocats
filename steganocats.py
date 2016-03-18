import json
import random


import flickrapi
from PIL import Image, ImageDraw, ImageFont

SECRETS_FILE = 'steganocats.json'


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


def get_flickr_photos(FlickrAPI_obj, terms, is_commons=True):
    ''' Query instantiated FlickrAPI object for terms'''
    photo_json = FlickrAPI_obj.photos.search(terms)
    return photo_json


# PIL functions for processing image
def to_greyscale(image_filename):
    ''' Convert a full-color image into a greyscale image.'''
    gs = Image.open(image_filename).convert('L')
    return gs


def write_steg(img_obj, phrase):
    ''' Returns image with hazburger phrase superimposed on it.'''
    x, y = img_obj.size
    x_insert, y_insert = x // 2, 2 * y // 3
    size = y // 10
    font = ImageFont.truetype('impact.ttf', size=size)
    draw = ImageDraw.Draw(img_obj)
    draw.text((x_insert, y_insert), phrase, font=font, fill='white')
    return img_obj


def make_flag(x_width, message, flag=b'\n'):
    ''' Given x-width of image and message, return prefix bytes for message.'''
    # Get bytes needed to represent length of message
    byte_len, overflow_bits = divmod(len(message).bit_length(), 8)
    if overflow_bits: byte_len += 1
    
    # If x_width not greater than len(message) + byte_len + null byte end flag
    # Throw an error
    assert x_width > len(message) + byte_len + 1

    return flag + len(message).to_bytes(byte_len, byteorder='little') + b'\x00'


def draw_pix(img_obj, message, pos=None):
    ''' Get horiz strip of pixels from img_obj.'''
    x, y = img_obj.size
    
    # Make insertion flag
    try:
        flag = make_flag(x, message)
    except:
        raise ValueError('Message will not fit in image.')
    
    # Write to bottom of image of no position specified
    if not pos:
        pos = y - 1

    pixels = img_obj.load()
    # Randomize bottom row of pixels.
    for px in range(x):
        pixels[px, pos] = random.randint(0, 255)

    # Write flag
    for px in range(0, len(flag)):
        pixels[px, pos] = flag[px]

    # Get step for writing pixels
    step = (x - len(flag)) // len(message)
    i = 0  # There likely is a Pythonic way to do this... but
    for px in range(len(flag), x, step):
        try:
            pixels[px, pos] = ord(message[i])
        except:
            break
        i += 1
    pass


def read_pix(img_obj, check_byte=b'\n', pos=None):
    ''' Find hidden message in an image.'''
    x, y = img_obj.size
    if not pos:
        pos = y - 1

    # Get strip of pixels that encode message from image.
    pixels = img_obj.load()
    pix_strip = [pixels[px, pos] for px in range(x)]
    if not pix_strip[0] == ord(check_byte):
        raise ValueError('Check byte not found.')

    # Find length of message.
    idx, count = 1, []
    while True:
        if not pix_strip[idx] == 0x00:
            count.append(pix_strip[idx])
            idx += 1
        else:
            idx += 1
            break
    else:
        raise ValueError('End flag not found.')
    message_len = int.from_bytes(count, byteorder='little')
    step = (x - idx) // message_len
    message_pixels = [chr(pix_strip[x]) for x in range(idx, x, step)]
    return message_pixels







flickr = make_flickr_api(SECRETS_FILE)

grey_kitty = to_greyscale('kitten.jpg')
grey_kitty_stegged = write_steg(grey_kitty, 'katz r kewl')
kitty = Image.open('kitten.jpg')
grey_pix = draw_pix(grey_kitty_stegged, "This is like a hidden message." * 5 )
grey_kitty_stegged.save('gks-stripes.jpg')

print(''.join(read_pix(grey_kitty_stegged)))

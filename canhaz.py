#!/usr/bin/env python3

import random 

from PIL import Image, ImageDraw, ImageFont


class canHaz:
    ''' Bag of methods for hiding messages in cat memes.'''

    def __init__(self, mode='L', flag=b'\n'):
        self.mode = mode
        self.flag = flag

    def _open_img(self, img_filename, mode=None):
        ''' Open an image and convert it to the selected mode.

            If no mode passed, defaults to instance attribute.'''
        if not mode: mode = self.mode
        return Image.open(img_filename).convert(mode)

    def _make_flag_bytes(self, x_width, hidden, flag=None):
        ''' Given image x_width and hidden data, return prefix bytes to mark
            row where hidden data encoded.
            
            This can be modified as necessary, but the _check_flag() method
            must be updated as well. '''
        # Get bytes needed to represent length of hidden
        byte_len, overflow_bits = divmod(len(hidden).bit_length(), 8)
        if overflow_bits: byte_len += 1
        
        # Get flag byte from state if none provided in arguments
        if not flag: flag = self.flag

        # If x_width not enuf to hold len(hidden) + byte_len + null byte 
        # throw an error
        assert x_width > len(hidden) + byte_len + 1

        return flag + len(hidden).to_bytes(byte_len, byteorder='little') + b'\x00'

    def _find_flag_bytes(img_obj, flag=None):
        ''' If row of encoding unknown, search image for flag bytes.'''
        if not flag:
            f = self.flag
        else:
            f = flag
        x, y = img_obj.size
        pixels = img_obj.load()
        hits = [y for y in range(f) if pixels[0, y] == f]
        return hits


    def write_meme(self, img_filename, phrase):
        ''' Returns image with hazburger phrase superimposed on it.'''
        img_obj = self._open_img(img_filename)
        x, y = img_obj.size
        x_insert, y_insert = x // 2, 2 * y // 3
        size = y // 10
        font = ImageFont.truetype('impact.ttf', size=size)
        draw = ImageDraw.Draw(img_obj)
        draw.text((x_insert, y_insert), phrase, font=font, fill='white')
        return img_obj

    def hide_msg(self, img_obj, hidden, mode=None, pos=None):
        ''' Randomize x pixels at y height, then encode hidden data into that
            row.

            mode => defaults to instance variable
            pos => defaults to the bottom row of the image
        '''
        x, y = img_obj.size
        if not mode:  # if no mode passed, default to instance variable.
            mode = self.mode

        # Make insertion flag
        try:
            f = self._make_flag_bytes(x, hidden)
        except Exception as E:
            print('Exception caught:', E)
            raise ValueError('Message will not fit in image.')    

        pixels = img_obj.load()
        if not pos:  # Write to bottom row of image of no position specified
            pos = y - 1
        for px in range(x):  # Randomize target row of pixels.
            pixels[px, pos] = random.randint(0, 255)
        for px in range(0, len(f)):  # Write flag bytes
            pixels[px, pos] = f[px]
        step = (x - len(f)) // len(hidden)  # Get step for writing pixels

        #  Encode message
        i = 0
        for px in range(len(f), x, step):
            try:
                pixels[px, pos] = ord(hidden[i])
            except:
                break
            i += 1
        pass

    def find_msg(self, img_obj, pos=None):
        ''' Find hidden message in an image.'''
        x, y = img_obj.size
        if not pos:
            pos = y - 1

        # Get strip of pixels that encode message from image.
        pixels = img_obj.load()
        pix_strip = [pixels[px, pos] for px in range(x)]
        if not pix_strip[0] == ord(self.flag):
            raise ValueError('Check byte not found.')

        # Find length of message
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
        # Get step of embedding and retrieve message.
        message_len = int.from_bytes(count, byteorder='little')
        step = (x - idx) // message_len
        message_pixels = [chr(pix_strip[x]) for x in range(idx, x, step)]
        return ''.join(message_pixels[:message_len])

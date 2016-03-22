#!/usr/bin/env python3

import random 

from PIL import Image, ImageDraw, ImageFont


class MemeWriter:
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

    def _find_row(img_obj, flag=None):
        ''' If row of encoding unknown, search image for flag bytes.'''
        if not flag:
            f = self.flag
        else:
            f = flag
        x, y = img_obj.size
        pixels = img_obj.load()
        hits = [y for y in range(f) if pixels[0, y] == f]
        if len(hits) > 1:
            print('More than one possible rows.')
            pass
        return hits[0]

    def _get_size(self, draw_obj, x, phrase, size=20):
        ''' Return best font size for phrase given x width of image'''
        font = ImageFont.truetype('impact.ttf', size=size)
        text_x, text_y = draw_obj.textsize(phrase, font)
        if text_x < x * 8 // 10:
            return self._get_size(draw_obj, x, phrase, size + 1)
        else: 
            return size

    @staticmethod
    def _set_border(x):
        ''' Set pixel size for text border based of img x width.'''
        if x < 1000:
            return 1
        elif x < 1500:
            return 2
        elif x < 3000:
            return 3
        else:
            return 4

    def write_meme(self, img_filename, phrase):
        ''' Returns image with hazburger phrase superimposed on it.'''
        img_obj = self._open_img(img_filename)
        x, y = img_obj.size
        x_insert, y_insert = x // 10, 4 * y // 5
        draw = ImageDraw.Draw(img_obj)
        size = self._get_size(draw, x, phrase)
        font = ImageFont.truetype('impact.ttf', size=size)
        # draw borders
        b = self._set_border(x) 
        draw.text((x_insert-b, y_insert), phrase, font=font, fill='black')
        draw.text((x_insert, y_insert-b), phrase, font=font, fill='black')
        draw.text((x_insert-b, y_insert+b), phrase, font=font, fill='black')
        draw.text((x_insert+b, y_insert), phrase, font=font, fill='black')
        draw.text((x_insert, y_insert+b), phrase, font=font, fill='black')
        draw.text((x_insert+b, y_insert-b), phrase, font=font, fill='black')
        # draw fill
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
        if not pos:  # Write to bottom row of image of no position specified
            pos = y - 1

        # Make insertion flag
        try:
            f = self._make_flag_bytes(x, hidden)
        except Exception as E:
            raise ValueError('Message will not fit in image.')
        # load image pixels
        pixels = img_obj.load()

        # In black and white images, only one byte per pix
        if mode == 'L':
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

        # RGBA images on the other hand have 4 bytes per pixel:
        elif mode == 'RGBA':
            for px in range(x):  # Randomize target row of pixels.
                r, g, b, a = pixels[px, pos]
                new_a = random.randint(0, 255)
                pixels[px, pos] = (r, g, b, new_a)
            for px in range(0, len(f)):  # Write flag bytes
                r, g, b, a = pixels[px, pos]
                new_a = f[px]
                pixels[px, pos] = (r, g, b, new_a)
            step = (x - len(f)) // len(hidden)  # Get step for writing pixels

            #  Encode message
            i = 0
            for px in range(len(f), x, step):
                try:
                    r, g, b, a = pixels[px, pos]
                    new_a = ord(hidden[i])
                    pixels[px, pos] = (r, g, b, new_a)
                except:
                    break
                i += 1
            pass

        else:
            raise AttributeError('Only greyscale and RGBA imges supported.')

    def find_msg(self, img_obj, pos=None, mode=None):
        ''' Find hidden message in an image.'''
        x, y = img_obj.size
        if not pos:
            pos = y - 1
        if not mode:  # if no mode passed, default to instance variable.
            mode = self.mode

        # Get strip of pixels that encode message from image.
        pixels = img_obj.load()
        pix_strip = [pixels[px, pos] for px in range(x)]

        # For black and white images (one byte for pixel)
        if mode == 'L':
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

            if not pix_strip[0] == ord(self.flag):
                raise ValueError('Check byte not found.')

        elif mode == 'RGBA':
            if not pix_strip[0][3] == ord(self.flag):
                raise ValueError('Check byte not found.')
            # Find length of message
            idx, count = 1, []
            while True:
                if not pix_strip[idx][3] == 0x00: 
                    count.append(pix_strip[idx][3])
                    idx += 1
                else:
                    idx += 1
                    break
            else:
                raise ValueError('End flag not found.')
            # Get step of embedding and retrieve message.
            message_len = int.from_bytes(count, byteorder='little')
            step = (x - idx) // message_len
            message_pixels = [chr(pix_strip[x][3]) for x in range(idx, x, step)]
            return ''.join(message_pixels[:message_len])

        else:
            raise AttributeError('Unsupported photo mode')

def main():
    ''' Some debug tests for when this is being put together'''
    msg = ''' The Naming of Cats is a difficult matter,
              It isn't just one of your holiday games;
              You may think at first I'm as mad as a hatter
              When I tell you, a cat must have THREE DIFFERENT NAMES.'''
    meme_writer = MemeWriter(mode='RGBA')
    steganocat = meme_writer.write_meme('kitten.jpg', 'Steganocats hide yr things'.upper())
    meme_writer.hide_msg(steganocat, msg)
    steganocat.save('written_cat.jpg')
    print(meme_writer.find_msg(steganocat))

if __name__ == '__main__':
    main()
![Steganokitty is Cute](https://github.com/jake-jake-jake/steganocats/blob/master/STEGANOCATS.jpg)
# STEGANOCATS HIDES YOUR THINGS

Steganocats is cat meme-maker with a twist: it conceals arbitrary bytes in the images it generates. Why you would want to do this is for you to figure out&mdash;maybe you only want your friends to know where the clubhouse is, maybe your sense of irony operates in strange dimensions&mdash;but if you do, Steganocats will make the whole process, from fetching images to meme-ifying them, as easy and fun as a bag of cats.

## Base Images

Steganocats draws a random image from the `base_images/` directory to use for the base image of the meme. Use something other than this adorable furball in your own projects.

### Getting Images from Flickr

Steganocats relies on the `flickrapi` package to query Flickr for images. This is an optional step; you can use whatever images you want with Steganocats by putting them in the `base_images/` directory. But querying Flickr for rights free photos that have been tagged by attention-hungry amateur photographers is a fun and easy way to find JPGs for your needs. We (that is, I, Jake) like cats&mdash;[the internet is for cats](https://en.wikipedia.org/wiki/Cats_and_the_Internet)&mdash;so Steganocats defaults to searching for `cat`.

To query Flickr for images, you will need a [Flickr API key](https://www.flickr.com/services/api/). Once you have one, add it to `_secrets.json` and then remove the underscore, so that it is named `secrets.json`. Voilà, you may now find many cats. 

## MemeWriter class

The `MemeWriter` class is a bag of methods for hiding messages in memes. It delegates the heavy lifting of image manipulation to `Pillow`, and I have done my best to make sure you don't have to know a thing about image files or `Pillow` classes to make your memes. Each instance of `MemeWriter` has a `mode` and a `flag` attribute, which control the mode of the output image and the byte that is encoded to flag the location of the hidden data. `MemeWriter` has three main methods: `write_meme` for creating memes, and `hide_msg` and `find_msg` for concealing and uncovering hidden bytes.

### mode

In order to conceal bytes, the `mode` attribute must be set to `L` (greyscale) or `RGBA` (four-channel JPG). If you're interested in why this is or how the bytes are ensconced, I have detailed the process in the code.

### flag
The `flag` attribute is the byte `MemeWriter` uses to mark the first pixel of a row it is encoding hidden bytes into. It defaults to `\n`.

### write_meme

`write_meme` takes two arguments, `fp`, a file object or file-like object representing the image to be manipulated, and `phrase`, the text to be meme-ified.

### hide_msg and find_msg

These two messages currently taken a `Pillow` image object as an argument; they will be refactored to take a `fp`, as with `write_meme`. `hide_msg` takes `hidden` as an argument; `hidden` should be a byteliteral.

## Steganography is not cryptography

Obligatory note that steganography is not encryption; you shouldn't count on the obscurity of your hidden message keeping it secure. That said, Steganocats will happily hide your encrypted bytes in kitty memes.

Photo: [meliha tunckanat](https://www.flickr.com/photos/tunckanat/4729470797/) 

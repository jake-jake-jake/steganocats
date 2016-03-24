![Steganokitty is Cute](https://github.com/jake-jake-jake/steganocats/blob/master/STEGANOCATS.jpg)
# STEGANOCATS HIDES YOUR THINGS

Steganocats is cat meme-maker with a twist: it conceals arbitrary bytes in the images it generates. Why you would want to do this is for you to figure out&mdash;maybe you only want your friends to know where the clubhouse is, maybe your sense of irony operates in strange dimensions&mdash;but if you do, Steganocats will make the whole process, from fetching images to meme-ifying them, as easy and fun as a bag of cats.

## Base Images

Steganocats draws a random image from the `base_images/` directory to use for the base image of the meme. The default image is XXX, taken from XXX, and used under CC license XXX. Use something other than this adorable furball in your own projects.

### Getting Images from Flickr

Steganocats relies on the flickrapi package to query Flickr for images. This is an optional step; you can use whatever images you want with Steganocats. But querying Flickr for that have arbitrary tags is very easy. We (that is, I) like cats, and the internet is for cats, so Steganocats defaults to searching for `cats`.

To query Flickr for images, you will need a [Flickr API key](https://www.flickr.com/services/api/). Once you have one, add it to `_secrets.json` and then remove the underscore: `secrets.json`.

## MemeWriter class

The MemeWriter class is a bag of methods for hiding messages in cat memes. It delegates the heavy lifting of image manipulation to Pillow. Each instance of MemeWriter has a `mode` and a `flag` attribute; the main methods employed are `write_meme` for creating memes, and `hide_msg` and `find_msg` for concealing bytes.

### mode

In order to conceal bytes, the mode must be `L` or `RGBA`. If you're interested in why this is or how the message is encoded, details are spelled out in comments in the code.

### flag
The `flag` attribute is the byte MemeWriter uses to mark the first pixel of a row it is encoding hidden bytes into. It defaults to `\n`.

### write_meme

`write_meme` takes two args, `img_filename`, the filename of the image file to be writte, and `phrase`, the text to be meme-ified.

### hide_ and find_msg

These two messages currently taken a Pillow image object as an argument; I may change this to an image filename in the future. hide_msg takes `hidden` as an argument; `hidden` should be a byteliteral.

## Steganography is note cryptography

Obligatory note that steganography is not encryption; but STEGANOCATS will happily hide your encrypted data in kitty pix.

Photo: [meliha tunckanat](https://www.flickr.com/photos/tunckanat/4729470797/) 







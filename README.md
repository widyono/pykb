# pykb
simple keyboard interaction program for toddler gameplay

requirements: pygame and Pillow modules, python v3

default setup will create media directories for allowed keys, look for Monaco
or Keyboard True Type Font, and create images for the allowed keys that will
be displayed when the associated key is pressed.

{pykb-media}/a/ will contain a.png, and be displayed when you press the 'A' key.

you can add other images that will be randomly selected when 'A' is pressed. just
add them to {pykb-media}/a/; they should be image types supported by pygame
(ideally PNG).

you can also add sound files that will be played simultaneously. OGG vorbis appears
to be the best supported file format by pygame. sound files should be named
according to the image that they will be played alongside. for example, if you
have {pykb-media}/a/airplane.png, the sound of an airplane should be saved as
{pykb-media}/a/airplane.ogg.

you can have multiple sound files for a single image; just add a colon and an
arbitrary suffix, such as {pykb-media}/a/airplane:noise.ogg.

if there is no sound file with the same basename as an image, but a sound file
does exist for the key name (e.g. {pykb-media}/a/airplane.png exists,
{pykb-media}/a/airplane.ogg does not, and {pykb-media}/a/a.ogg does), then
the key name's sound file will be played instead.

for osx, one method of recording your own sound files would be:

use quicktime's New Audio Recording option to record an audio clip, and save it
somewhere temporary (it will save inside an .m4a container). use ffmpeg to
convert that to ogg (ffmpeg -i "${1}" -c:a libvorbis -qscale:a 5 "${1%%.m4a}.ogg")
and then use audacity to clean up the clip (remove quiet parts before and after,
for example) and save to {pykb-media}/a/airplane.ogg (for example)

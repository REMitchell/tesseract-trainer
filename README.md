# tesseract-trainer
This is a set of two tools used to generate OCR training files for Tesseract. It is particularly designed for image files with small numbers of characters. It will help you create box files, assuming the name of the image file reflects the text contained in the image. 

To run the tesseract trainer, you need to point it at a directory containing a set of image files and a set of box files with corresponding file names. e.g. You might have a directory containing:
- asdf.png
- asdf.box
- qwerty.png
- qwerty.box

Where the file names correspond to the characters that the image contains.

This will produce a trained font file "traineddata.cap" (if you're using the default font name 'cap')

Put this file in /usr/local/share/tessdata to make the font available

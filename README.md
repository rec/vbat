# VBAT

Welcome to the VBAT (video based antenna tracker) project.
You'll find the main project at https://github.com/Jazzkeller/VBAT.

How it works:
vbat-config:
- Start vbat-config. 
- Import test images per file or webcam. These test images have to be taken with black camera input, so that only the OSD is visible. 
- Select the latitude and longitude fields to find at which position the characters will show up in the stream.
- Sort pictures to to right characters 
- Create a template for each character
- Find the fields for the hight value by selecting the last number for the hight in the image.

vbat:
- Start vbat -n NAME (NAME is the seassion name you give in vbat-config).
- You get an output with the recognised values for latutude, longitude an hight.
Or:
- Start vbat -NAME -i TEST.JPG (TEST.JPG is a picture grabbed from the video stream). vbat -n zz -i test.jpeg runs the current test-scenario.
- You get an output with the recognised values for latutude, longitude an hight.

There are images to create the fields (black camera image with OSD overlay) and test images in the folder "images"

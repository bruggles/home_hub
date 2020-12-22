from picamera import PiCamera
from time import sleep

camera = PiCamera()
#camera.rotation = 180
camera.resolution = (1920, 1080) #max still resolution is 2592x1944, max video resolution is 1920x1080 
camera.framerate = 15 #this is about as fast as it can go on video with full resoution
#camera.brightness = 70 #default is 50, range is from 0-100
#camera.contrast = 50 #default = 50, range is from 0-100
#camera.exposure_mode = auto #other options = off, night, nightpreview, backlight, spotlight,sports, snow, beach, verylong, fixedfps, antishake, fireworks
#camera.awb_mode = auto #white balance modes = off, sunlight, cloudy, shade, tungsten, flourescent, incancescent, flash, horizon


#code to display preview
#camera.start_preview()
#sleep(5)
#camera.stop_preview()

#take a picture
#camera.annotate_text = "today's date"
#camera.annotate_text_size = 50
camera.capture('path/image.jpg')

#record video
camera.start_recording('path/video.h264')
sleep(5)
camera.stop_recording()


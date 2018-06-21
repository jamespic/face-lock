#!/usr/bin/python2
import cv2
import dbus
import time
from monotonic import monotonic

frame_time = 0.5
lock_time = 8.0

if __name__ == '__main__':
    frontal_cascade = cv2.CascadeClassifier(
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
#        '/usr/share/opencv/lbpcascades/lbpcascade_frontalface.xml'
    )
    profile_cascade = cv2.CascadeClassifier(
        '/usr/share/opencv/haarcascades/haarcascade_profileface.xml'
#        '/usr/share/opencv/lbpcascades/lbpcascade_profileface.xml'
    )
    video_capture = cv2.VideoCapture(0)

    bus = dbus.SessionBus()
    lock_proxy = bus.get_object(
        'com.canonical.Unity', '/com/canonical/Unity/Session')


    face_last_seen = monotonic()

    while True:
        if not video_capture.isOpened():
            print "Unable to load camera"


        for i in xrange(4):
            video_capture.grab()
        success, frame = video_capture.read()
        if not success:
            print "Couldn't capture frame"

        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = []

        if len(frontal_cascade.detectMultiScale(
                grey, scaleFactor=1.1, minNeighbors=4)):
            faces.append('frontal')

        if len(profile_cascade.detectMultiScale(
                grey, scaleFactor=1.1, minNeighbors=4)):
            faces.append('left profile')

        flipped = cv2.flip(grey, 1)
        if len(profile_cascade.detectMultiScale(
                flipped, scaleFactor=1.1, minNeighbors=4)):
            faces.append('right profile')

        if len(faces):
            print "Faces detected:", ', '.join(faces)
            face_last_seen = monotonic()
        else:
            print "Faces not detected"

        if monotonic() > face_last_seen + lock_time:
            lock_proxy.Lock(dbus_interface='com.canonical.Unity.Session')
            face_last_seen = monotonic()

        time.sleep(frame_time)

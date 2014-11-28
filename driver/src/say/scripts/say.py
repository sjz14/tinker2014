#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File          : say.py
# Author        : bss
# Creation date : 2014-07-21
#  Last modified: 2014-07-22, 00:00:49
# Description   : say something through loudspeaker.
#

import sys
import os
import time
import getopt
import rospkg
import rospy
from std_msgs.msg import String

def getSpeechCallback(data):
    print(data.data)
    playSound(data.data)

def Usage():
    print('say.py usage:')
    print('speak')
    print('ros topic: /say')


def playSound(sent):
    mp3dir = rospkg.RosPack().get_path('say') + '/resource/sounds/'
    if os.path.exists(mp3dir + sent + '.mp3'):
        os.system('mplayer "' + mp3dir + sent + '.mp3"')
    else:
        sent_speak = sent.replace("'", '')
        os.system("espeak -s 130 --stdout '" + sent_speak + "' | aplay")

def main(argv):
    # Listen to /say
    rospy.init_node('say_node', anonymous=True)
    rospy.Subscriber('/say', String, getSpeechCallback)
    rospy.spin()

if __name__ == '__main__':
    main(sys.argv)


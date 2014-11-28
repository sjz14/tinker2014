#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File          : fetch_google.py
# Author        : bss
# Creation date : 2014-05-10
#  Last modified: 2014-07-20, 02:43:12
# Description   : Hacking google tts api
#

import sys
import os
import rospkg

def getAnswerSpeech(answer):
    script = rospkg.RosPack().get_path('answer_questions') + '/scripts/Google-Translate-TTS/GoogleTTS.py'
    mp3dir = rospkg.RosPack().get_path('answer_questions') + '/resource/sounds/'
    #answer.replace("'", r"\'")
    os.system('python ' + script
            + ' -o ' +  '"' + mp3dir + answer + '.mp3"'
            + ' -s ' + '"' + answer + '"')

def main(argv):
    rcdir = rospkg.RosPack().get_path('answer_questions') + '/resource/'
    # answer
    fp = open(rcdir + 'answers.txt', 'r')
    for line in fp.readlines():
        sentence = line.strip()
        if sentence != '':
            getAnswerSpeech(str(sentence))
    fp = open(rcdir + 'questions.txt', 'r')
    for line in fp.readlines():
        sentence = line.strip()
        if sentence != '':
            getAnswerSpeech(str(sentence))
    fp.close()
    
if __name__ == '__main__':
    main(sys.argv)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File          : answer_node.py
# Author        : bss
# Creation date : 2014-05-09
#  Last modified: 2014-07-22, 20:34:18
# Description   : Answer question listed in resource/
#

import sys
import os
import time
import getopt
import rospkg
import rospy
from std_msgs.msg import String
from std_srvs.srv import *

ANS = {}
say_pub = rospy.Publisher('/say', String)

class answer_handler:
    def __init__(self):
        self.allow = True
        self.force_allow = False
        self.count = 0

    def start(self, req):
        print('start working')
        self.allow = True
        self.count = 0
        return EmptyResponse()

    def stop(self, req):
        if self.force_allow:
            return
        print('stop working')
        self.allow = False
        return EmptyResponse()

    def getQuestionCallback(self, data):
        if not self.force_allow:
            if not self.allow:
                print('job stopped.')
                return

        ques = str(data.data).strip()

        # ping
        if 'how are you tinker how are you tinker' == ques:
            playSound('I hear you.')
            return

        try:
            ans = ANS[ques.upper()]
        except:
            print("I can't answer your question: " + ques)
            print('Make sure you use the correct launch file in pocketsphinx.')
            sys.exit(1)
        print(ques + '?')
        print('-' + ans)
    
        try:
            answer_once = rospy.ServiceProxy('/answer/answer_once', Empty)
            answer_once()
        except rospy.ServiceException, e:
            print("Service call failed: %s"%e)

        #stop recognizer
        try:
            stop_pock = rospy.ServiceProxy('/recognizer/stop', Empty)
            stop_pock()
        except rospy.ServiceException, e:
            print("Service call failed: %s"%e)

        playSound('Your question is:')
        playSound(ques)
        playSound('My answer is:')
        if ques == 'what time is it':
            hour = int(time.strftime('%H'))
            hour = (hour + 1) % 12
            minute = int(time.strftime('%M'))
            ans = str(hour) + ' ' + str(minute)
            print(ans)
            playSound(ans)
        else:
            playSound(ans)
        
        self.count += 1
        if self.count >= 3:
            self.allow = False
        if self.allow or self.force_allow:
            playSound('Please continue.')
        else:
            playSound('Thank you for your questions. Goodbye.')

        #start recognizer
        try:
            start_pock = rospy.ServiceProxy('/recognizer/start', Empty)
            start_pock()
        except rospy.ServiceException, e:
            print("Service call failed: %s"%e)


def Usage():
    print('answer_node.py usage:')
    print('回答问题')
    print('-h,--help: print help message.')
    print('-i: no num limit.')

def playSound(answer):
    say_pub.publish(answer)

def main(argv):
    try:
        opts, argv = getopt.getopt(argv[1:], 'hi', ['help'])
    except getopt.GetoptError, err:
        print(str(err))
        Usage()
        sys.exit(2)
    except:
        Usage()
        sys.exit(1)

    ah = answer_handler()

    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(0)
        if o in ('-i'):
            ah.force_allow = True

    rcdir = rospkg.RosPack().get_path('answer_questions') + '/resource/'
    # question
    fp = open(rcdir + 'questions.txt', 'r')
    ques = []
    for line in fp.readlines():
        sentence = line.strip().upper()
        if sentence != '':
            ques.append(str(sentence))
    fp.close()
    # answer
    fp = open(rcdir + 'answers.txt', 'r')
    ans = []
    for line in fp.readlines():
        sentence = line.strip()
        if sentence != '':
            ans.append(str(sentence))
    fp.close()
    
    for i in range(0, min(len(ques), len(ans))):
        ANS[ques[i]] = ans[i]
    print(str(len(ANS)) + ' q&a find.')
    
    ah.stop(None)

    # Listen to /recognizer/output from pocketsphinx, task:answer
    rospy.init_node('answer_node', anonymous=True)
    rospy.Subscriber('/recognizer/output', String, ah.getQuestionCallback)
    rospy.Service("/answer/start", Empty, ah.start)
    rospy.Service("/answer/stop", Empty, ah.stop)
    rospy.spin()

if __name__ == '__main__':
    main(sys.argv)


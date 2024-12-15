#!/usr/bin/env python3

# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

import json
from pynput import keyboard

from RcBrainThread import RcBrainThread
from std_msgs.msg import String
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from experimentalDetector import Detector
import numpy as np
import time
import cv2


import rospy

class RemoteControlTransmitterProcess():
    # ===================================== INIT==========================================
    def __init__(self):
        """Run on the PC. It forwards the commans from the user via KeboardListenerThread to the RcBrainThread. 
        The RcBrainThread converts them into actual commands and sends them to the remote via a socket connection.
        
        """
        self.dirKeys   = ['w', 'a', 's', 'd']
        self.paramKeys = ['t','g','y','h','u','j','i','k', 'r', 'p']
        self.pidKeys = ['z','x','v','b','n','m']

        self.allKeys = self.dirKeys + self.paramKeys + self.pidKeys
        self.bridge = CvBridge()
        self.cvImage = np.zeros((640, 480))
        rospy.Subscriber("/automobile/rcCar/camera_follow/image_raw", Image, self.callback)
        self.rcBrain   =  RcBrainThread()   
        
        rospy.init_node('EXAMPLEnode', anonymous=False)     
        self.publisher = rospy.Publisher('/automobile/command', String, queue_size=1)

    def callback(self, data):
        self.cvImage = self.bridge.imgmsg_to_cv2(data, "bgr8")
        
    def auto(self):
        
        data_speed = {}
        data_steer ={}
        rate = rospy.Rate(10)
        speed = 10.0
        steer = 0.0
        data_speed['action']        =  '1'
        data_speed['speed']    =  float(speed/100.0)
        data_steer['action']        =  '2'
        data_steer['steerAngle']    =  float(steer)
        while not rospy.is_shutdown():
            if self.cvImage is not None:
                steel_recv = self.img_proccessor(self.cvImage)
                # New function to process image here
                print('steer angle: %f' % steel_recv, end = '\r')
            data_speed['speed']    =  float(speed/100.0)
            if steel_recv is not None:
                data_steer['steerAngle'] = float(steel_recv)
            else:
                data_steer['steerAngle'] = 0.0  # hoặc bất kỳ giá trị nào phù hợp khác
            command_sp=json.dumps(data_speed)
            command_st=json.dumps(data_steer)

            # rospy.loginfo("sp:%f",speed)
            # rospy.loginfo("st:%f",steer)
            self.publisher.publish(command_sp)
            self.publisher.publish(command_st)
            cv2.waitKey(1)
            rate.sleep()
        cv2.destroyAllWindows()

    def img_proccessor(self, frame_image):
        self.last_time = time.time()
        steerAngle = laneDetector.detection(frame_image)
        
        return -(steerAngle - 90)

    # ===================================== RUN ==========================================
    def run(self):
        """Apply initializing methods and start the threads. 
        """
        with keyboard.Listener(on_press = self.keyPress, on_release = self.keyRelease) as listener: 
            listener.join()
	
    # ===================================== KEY PRESS ====================================
    def keyPress(self,key):
        """Processing the key pressing 
        
        Parameters
        ----------
        key : pynput.keyboard.Key
            The key pressed
        """                                     
        try:                                                
            if key.char in self.allKeys:
                keyMsg = 'p.' + str(key.char)

                self._send_command(keyMsg)
    
        except: pass
        
    # ===================================== KEY RELEASE ==================================
    def keyRelease(self, key):
        """Processing the key realeasing.
        
        Parameters
        ----------
        key : pynput.keyboard.Key
            The key realeased. 
        
        """ 
        if key == keyboard.Key.esc:                        #exit key      
            self.publisher.publish('{"action":"3","steerAngle":0.0}')   
            return False
        try:                                               
            if key.char in self.allKeys:
                keyMsg = 'r.'+str(key.char)

                self._send_command(keyMsg)
    
        except: pass                                                              
                 
    # ===================================== SEND COMMAND =================================
    def _send_command(self, key):
        """Transmite the command to the remotecontrol receiver. 
        
        Parameters
        ----------
        inP : Pipe
            Input pipe. 
        """
        command = self.rcBrain.getMessage(key)
        if command is not None:
	
            command = json.dumps(command)
            self.publisher.publish(command)  
            
if __name__ == '__main__':
    laneDetector = Detector()

    try:
        nod = RemoteControlTransmitterProcess()
        nod.auto()
    except rospy.ROSInterruptException:
        pass
# https://stackoverflow.com/questions/7207309/how-to-run-functions-in-parallel
from __future__ import print_function
import os
import time
from multiprocessing import Process
from typing import List, Tuple, Union
from subprocess import Popen, PIPE, STDOUT

import cv2
import numpy as np

class Preprocess(object):
    
    def __init__(self, input_size, fill_value : int =128):
        """
        Initialize parametyers for preprocessing.
        Parameters
        ----------
        input_size : int or tuple
                     input dimensions of the input image
                     may be tuple of (H, W) or an int
        fill_value : int
                     Fill-in values for padding areas
        """
        self.input_size = input_size
        self.fill_value = fill_value

        if isinstance(self.input_size, List) or isinstance(self.input_size, Tuple):
            assert self.input_size[0] == self.input_size[1] , "Input weight and width are not the same."
            self.input_size = int(self.input_size[0])
    
    @staticmethod
    def _aspectaware_resize_padding(image, width, height, interpolation=None, means=None):
        """
        Pads input image without losing the aspect ratio of the original image
        Parameters
        ----------
        image         : numpy array
                        In BGR format
                        uint8 numpy array of shape (img_h, img_w, 3)
        width         : int
                        width of newly padded image
        height        : int
                        height of newly padded image
        interpolation : str
                        method, to be applied on the image for resizing
        
        Returns
        -------       
        canvas        : numpy array
                        float 32 numpy array of shape (height, width, 3)
        new_w         : int
                        width, of the image after resizing without losing aspect ratio
        new_h         : int
                        height, of the image after resizing without losing aspect ratio
        old_w         : int
                        width, of the image before padding
        old_h         : int
                        height, of the image before padding
        padding_w     : int
                        width, of the image after padding
        padding_h     : int
                        height, of the image after padding
        """

        old_h, old_w, _ = image.shape
        if old_w > old_h:
            new_w = width
            new_h = int(width / old_w * old_h)
        else:
            new_w = int(height / old_h * old_w)
            new_h = height
        
        # resize the image by maintaining aspect ratio
        if new_w != old_w or new_h != old_h:
            if interpolation is None:
                image = cv2.resize(image, (new_w, new_h))
            else:
                image = cv2.resize(image, (new_w, new_h), interpolation=interpolation)

        padding_h = height - new_h
        padding_w = width - new_w

        # parameter for inserting resized image to the middle of canvas
        h_start = max(0, height - new_h) // 2
        w_start = max(0, width - new_w) // 2

        # pad the resized-contrast ratio maintained image to get desired dimensions
        image = cv2.copyMakeBorder(image, h_start, h_start, w_start, w_start, cv2.BORDER_CONSTANT, value=[means, means, means])

        return image, new_w, new_h, old_w, old_h, padding_w, padding_h,

    def __call__(self, img):
        """
        Preprocess an image for YOLOv5 TensorRT model inferencing.
        Parameters
        ----------
        img         : numpy array
                      In BGR format
                      uint8 numpy array of shape (img_h, img_w, 3)
        
        Returns
        -------
        img         : numpy array
                      preprocessed image
                      float32 numpy array of shape (3, H, W)
        metas       : list
                      list containing additional informations about the image
        """
        # resize the image and pad the image by maintaining contrast ratio
        img_meta = self._aspectaware_resize_padding(image=img, width=self.input_size, 
                                            height=self.input_size, interpolation=cv2.INTER_LINEAR, means=self.fill_value)

        img = np.transpose(img_meta[0], (2, 0, 1)).astype(np.float32)
        img = np.expand_dims(img, axis=0)
        img /= 255.0

        return img

def extract_frames_ffmpeg(video_path, folder_path):
    print("Extracting frames from {}".format(video_path))

    abs_video_path = os.path.abspath(video_path)
    folder_path = "data/{:s}".format(folder_path)

    command = "ffmpeg -hide_banner -loglevel error -i {:s} {:s}/out-%04d.jpg".format(abs_video_path, folder_path)

    # Execute Command
    process = Popen(command, stdout=PIPE, shell=True, stderr=STDOUT, bufsize=1, close_fds=True)
    for line in iter(process.stdout.readline, b''):
        print(line.rstrip().decode('utf-8'))
    process.stdout.close()
    process.wait()

    print("Extracting frames from {:s} done!".format(abs_video_path))

def extract_preprocessed_frames_opencv(video_path, folder_name):
    print("Extracting frames from {}".format(video_path))

    abs_video_path = os.path.abspath(video_path)
    print(abs_video_path)
    folder_path = "data/{:s}".format(folder_name)
    preprocess_fn = Preprocess(input_size = 640)

    count = 0
    vidcap = cv2.VideoCapture(abs_video_path)

    while True:
        success, image = vidcap.read()

        if not success:
            print(success)
            break
        else:
            npy_path = "%s/out-%04d.npy" % (folder_path, count)
            npy = preprocess_fn(image)
            np.save(npy_path, npy)
            success,image = vidcap.read()
            count += 1

    print("Extracting and Preprocessing frames from {:s} done!".format(abs_video_path))

if __name__ == "__main__":

    start_time = time.time()

    process1 = Process(target=extract_preprocessed_frames_opencv, args=('videos/1.mp4', '1',))
    process2 = Process(target=extract_preprocessed_frames_opencv, args=('videos/2.mp4', '2',))
    process3 = Process(target=extract_preprocessed_frames_opencv, args=('/home/htut/Desktop/AsyncCV/videos/3.mp4', '3',))
    process4 = Process(target=extract_preprocessed_frames_opencv, args=('/home/htut/Desktop/AsyncCV/videos/4.mp4', '4',))

    process1.start()
    process2.start()
    process3.start()
    process4.start()


    process1.join()
    process2.join()
    process3.join()
    process4.join()
    
    end_time = time.time()

    print("Total elapsed time : {}".format(end_time - start_time))
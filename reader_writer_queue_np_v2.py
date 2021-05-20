"""
https://stackoverflow.com/questions/11515944/how-to-use-multiprocessing-queue-in-python

1. Classic Producer - Consumer problem (https://en.wikipedia.org/wiki/Producer%E2%80%93consumer_problem)
2. Python multiprocessing
3. Pytorch multiprocessing
4. Bounded Buffer problem
"""

import os
import sys
import time
from typing import List, Tuple
from multiprocessing import Process, Queue

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

def preprocessor_proc(video, queue):
    # Write the frames, read with opencv, to the queue
    video_path = os.path.abspath(video)

    vidcap = cv2.VideoCapture(video_path)
    # create an instance of the preprocess class
    preprocessor = Preprocess(input_size=640) 

    while True: 
        success, frame = vidcap.read()
        if not success:
            queue.put("DONE")
            break
        else:
            np_frame = preprocessor(frame)
            queue.put(np_frame)
            # print("Writer Queue Length : {}".format(queue.qsize()))

def batch_multiplex_proc(first_queue, second_queue):
    
    # Read from multiple queues, this will be spawned as a seperate process

    # make a batch numpy array and save it as a npy file
    count = 0
    first = True
    second = True

    while True:
        # get data from noth queue simultaneously
        if first and second:
            first_frame = first_queue.get()
            second_frame = second_queue.get()
        elif first and not second:
            first_frame = first_queue.get()
            second_frame = "DONE"
        elif not first and second:
            first_frame = "DONE"
            second_frame = second_queue.get()
        else:
            first_frame = "DONE"
            second_frame = "DONE"

        # Configure npy file path
        npy_path = "%s/%s/out-%04d.npy" % ("data", "queue", count)

        if isinstance(first_frame, np.ndarray) and isinstance(second_frame, np.ndarray):
            batch_array = np.vstack((first_frame, second_frame))
            np.save(npy_path, batch_array)
            count += 1
            print("Batch")
            print("Reader first queue length : {}".format(first_queue.qsize()))
            print("Reader second queue length : {}".format(second_queue.qsize()))
        elif isinstance(first_frame, np.ndarray) and second_frame == "DONE":
            batch_array = first_frame
            np.save(npy_path, batch_array)
            count += 1
            second = False
            print("Single")
            print("Reader first queue length : {}".format(first_queue.qsize()))
            print("Reader second queue length : {}".format(second_queue.qsize()))
        elif isinstance(second_frame, np.ndarray) and first_frame == "DONE":
            batch_array = second_frame
            np.save(npy_path, batch_array)
            count += 1
            first = False
            print("Single")
            print("Reader first queue length : {}".format(first_queue.qsize()))
            print("Reader second queue length : {}".format(second_queue.qsize()))
        else:
            break


if __name__=='__main__':
    fqueue = Queue()  # preprocessor_proc() writes to this queue associated with its video stream from _this_ process    
    squeue = Queue()  # preprocessor_proc() writes to this queue associated with its video stream from _this_ process    

    # Reader processes that write into it's respective queues
    stream1_p = Process(target=preprocessor_proc, args=("videos/1.mp4", fqueue, )) # send video path and queue as args to proc
    stream2_p = Process(target=preprocessor_proc, args=("videos/2.mp4", squeue, )) # send video path and queue as args to proc
    stream1_p.daemon = True
    stream2_p.daemon = True

    stream1_p.start() # Launch stream1 grasp/ preprocess operations as seperate python process since they are independent
    stream2_p.start() # Launch stream1 grasp/ preprocess operations as seperate python process since they are independent

    batch_p = batch_multiplex_proc(fqueue, squeue)

    stream1_p.join()
    stream2_p.join()
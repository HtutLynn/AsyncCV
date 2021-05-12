# https://stackoverflow.com/questions/7207309/how-to-run-functions-in-parallel

import os
from multiprocessing import Process
from subprocess import Popen, PIPE, STDOUT

import cv2

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

def extract_frames_opencv(video_path, folder_name):
    print("Extracting frames from {}".format(video_path))

    abs_video_path = os.path.abspath(video_path)
    folder_path = "data/{:s}".format(folder_name)

    vidcap = cv2.VideoCapture(abs_video_path)
    success,image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite("%s/out-%04d.jpg" % (folder_path, count), image)     # save frame as JPEG file      
        success,image = vidcap.read()
        count += 1

    print("Extracting frames from {:s} done!".format(abs_video_path))


def find_divisibles(inrange, div_by):
    print("finding nums in range {} divisible by {}".format(inrange, div_by))
    located = []
    for i in range(inrange):
        if i % div_by == 0:
            located.append(i)

    print("Done w/ nums in range {} divisible by {}".format(inrange, div_by))

if __name__ == "__main__":
    process1 = Process(target=extract_frames_opencv, args=('videos/1.mp4', '1',))
    process2 = Process(target=extract_frames_opencv, args=('videos/2.mp4', '2',))
    process3 = Process(target=extract_frames_opencv, args=('vidoes/3.mp4', '3',))
    process4 = Process(target=find_divisibles, args=(500, 3,))

    process1.start()
    process2.start()
    process3.start()
    process4.start()


    process1.join()
    process2.join()
    process3.join()
    process4.join()
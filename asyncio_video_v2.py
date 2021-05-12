import os
import asyncio
from subprocess import Popen, PIPE, STDOUT

import cv2

async def extract_frames_opencv(video_path, folder_name):
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


async def main():
    extract1 = loop.create_task(extract_frames_opencv(video_path="videos/1.mp4",
                                                      folder_name="1"))
    extract2 = loop.create_task(extract_frames_opencv(video_path="videos/2.mp4",
                                                      folder_name="2"))
    extract3 = loop.create_task(extract_frames_opencv(video_path="videos/3.mp4",
                                                      folder_name="3"))
    extract4 = loop.create_task(extract_frames_opencv(video_path="videos/4.mp4",
                                                      folder_name="4"))

    await asyncio.wait([extract1, extract2, extract3, extract4])

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(1)
        loop.run_until_complete(main())
    except Exception as e:
        print("lee")
        pass
    finally:
        loop.close()
import os
import asyncio
import multiprocessing
from subprocess import Popen, PIPE, STDOUT

from tqdm import tqdm

def extract_frames_ffmpeg(info):
    print("Extracting frames from {}".format(info[0]))

    abs_video_path = os.path.abspath(info[0])
    folder_path = "data/{:s}".format(info[1])

    command = "ffmpeg -hide_banner -loglevel error -i {:s} {:s}/out-%04d.jpg".format(abs_video_path, folder_path)

    # Execute Command
    process = Popen(command, stdout=PIPE, shell=True, stderr=STDOUT, bufsize=1, close_fds=True)
    for line in iter(process.stdout.readline, b''):
        print(line.rstrip().decode('utf-8'))
    process.stdout.close()
    process.wait()

    print("Extracting frames from {:s} done!".format(abs_video_path))

async def extract(infos):
    try:
        with multiprocessing.Pool(processes=4) as pool:
            pool.map(extract_frames_ffmpeg, infos)
        pool.close()

        return "Success"
    except Exception as e:
        print(e)
        print("Multiprocessing failed or Something is wrong with the code.")

async def find_divisibles(inrange, div_by):
    print("finding nums in range {} divisible by {}".format(inrange, div_by))
    located = []
    for i in range(inrange):
        if i % div_by == 0:
            located.append(i)
        # if i % 50000 == 0:
        #     await asyncio.sleep(0.0001)

    print("Done w/ nums in range {} divisible by {}".format(inrange, div_by))
    return located

async def main():

    infos = [["/home/htut/Downloads/Video/inferenced_videos/1.mp4", "1"],
             ["/home/htut/Downloads/Video/inferenced_videos/2.mp4", "2"],
             ["/home/htut/Downloads/Video/inferenced_videos/3.mp4", "3"],
             ["/home/htut/Downloads/Video/inferenced_videos/4.mp4", "4"]]

    extract1 = loop.create_task(extract(infos))
    divs1 = loop.create_task(find_divisibles(508000, 34113))
    
    await asyncio.wait([extract1, divs1])

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        # loop.set_debug(1)
        loop.run_until_complete(main())
    except Exception as e:
        print(e)
        pass
    finally:
        loop.close()
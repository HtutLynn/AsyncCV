import os
import asyncio
from subprocess import Popen, PIPE, STDOUT

async def extract_frames_ffmpeg(video_path, folder_name):
    print("Extracting frames from {}".format(video_path))

    abs_video_path = os.path.abspath(video_path)
    folder_path = "data/{:s}".format(folder_name)

    command = "ffmpeg -hide_banner -loglevel error -i {:s} {:s}/out-%04d.jpg".format(abs_video_path, folder_path)

    # Execute Command
    process = Popen(command, stdout=PIPE, shell=True, stderr=STDOUT, bufsize=1, close_fds=True)
    for line in iter(process.stdout.readline, b''):
        print(line.rstrip().decode('utf-8'))
    process.stdout.close()
    process.wait()

    print("Extracting frames from {:s} done!".format(abs_video_path))

async def main():
    extract1 = loop.create_task(extract_frames_ffmpeg(video_path="/home/htut/Downloads/Video/inferenced_videos/1.mp4",
                                                      folder_name="1"))
    extract2 = loop.create_task(extract_frames_ffmpeg(video_path="/home/htut/Downloads/Video/inferenced_videos/2.mp4",
                                                      folder_name="2"))
    extract3 = loop.create_task(extract_frames_ffmpeg(video_path="/home/htut/Downloads/Video/inferenced_videos/3.mp4",
                                                      folder_name="3"))
    extract4 = loop.create_task(extract_frames_ffmpeg(video_path="/home/htut/Downloads/Video/inferenced_videos/4.mp4",
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
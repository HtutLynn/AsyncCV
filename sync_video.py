import os
from subprocess import Popen, PIPE, STDOUT

def extract_frames_ffmpeg(video_path, folder_name):
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

def main():
    extract_frames_ffmpeg(video_path="videos/1.mp4",
                          folder_name="1")
    extract_frames_ffmpeg(video_path="videos/2.mp4",
                          folder_name="2")
    extract_frames_ffmpeg(video_path="videos/3.mp4",
                          folder_name="3")
    extract_frames_ffmpeg(video_path="videos/4.mp4",
                          folder_name="4")

if __name__ == "__main__":
    main()
    
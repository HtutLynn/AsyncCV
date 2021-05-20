import numpy as np
import subprocess as sp
import threading
import queue
import time

class CCTVReader(threading.Thread):
    def __init__(self, q, in_stream, chunk_size):
        super().__init__()
        self.q = q
        self.chunk_size = chunk_size
        self.command = ["ffmpeg",
                        "-c:v", "h264",     # Tell FFmpeg that input stream codec is h264
                        "-i", in_stream,    # Read stream from file vid.264
                        "-c:v", "copy",     # Tell FFmpeg to copy the video stream as is (without decoding and encoding)
                        "-an", "-sn",       # No audio an no subtitles
                        "-f", "h264",       # Define pipe format to be h264
                        "-"]                # Output is a pipe

    def run(self):
        pipe = sp.Popen(self.command, stdout=sp.PIPE, bufsize=1024**3)  # Don't use shell=True (you don't need to execute the command through the shell).

        # while True:
        for i in range(100):  # Read up to 100KBytes for testing
            data = pipe.stdout.read(self.chunk_size)  # Read data from pip in chunks of self.chunk_size bytes
            self.q.put(data)

            # Break loop if less than self.chunk_size bytes read (not going to work with CCTV, but works with input file)
            if len(data) < self.chunk_size:
                break

        try:
            pipe.wait(timeout=1)  # Wait for subprocess to finish (with timeout of 1 second).
        except sp.TimeoutExpired:
            pipe.kill()           # Kill subprocess in case of a timeout (there should be a timeout because input stream still lives).



#in_stream = "rtsp://xxx.xxx.xxx.xxx:xxx/Streaming/Channels/101?transportmode=multicast",

#Use public RTSP Streaming for testing
in_stream1 = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"

in_stream2 = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"


q1 = queue.Queue()
q2 = queue.Queue()

cctv_reader1 = CCTVReader(q1, in_stream1, 1024)  # First stream 
cctv_reader2 = CCTVReader(q2, in_stream2, 2048)  # Second stream

cctv_reader1.start()
time.sleep(5) # Wait 5 seconds (for testing).
cctv_reader2.start()

cctv_reader1.join()
cctv_reader2.join()

if q1.empty():
    print("There is a problem (q1 is empty)!!!")
else:
    # Write data from queue to file vid_from_queue1.264 (for testing)
    with open("vid_from_q1.264", "wb") as queue_save_file:
        while not q1.empty():
            queue_save_file.write(q1.get())

if q2.empty():
    print("There is a problem (q2 is empty)!!!")
else:
    # Write data from queue to file vid_from_queue2.264 (for testing)
    with open("vid_from_q2.264", "wb") as queue_save_file:
        while not q2.empty():
            queue_save_file.write(q2.get())
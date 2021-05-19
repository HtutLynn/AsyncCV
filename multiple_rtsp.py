import numpy as np
import subprocess as sp
import threading
import queue

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
        pipe = sp.Popen(self.command, stdout=sp.PIPE, bufsize=1024**2*100)

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


    def save_q_to_file(self, vid_file_name):
        # Write data from queue to file (for testing)
        if self.q.empty():
            print("There is a problem (q is empty)!!!")
        else:            
            with open(vid_file_name, "wb") as queue_save_file:
                while not self.q.empty():
                    queue_save_file.write(self.q.get())

#in_stream = "rtsp://xxx.xxx.xxx.xxx:xxx/Streaming/Channels/101?transportmode=multicast",

#Use public RTSP Streaming for testing
#in_stream = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"

#Use public RTSP Streaming for testing
readers = {}
queues = {}

# Read from file (for tesing)
dict = {
        "name1":{ "ip":"vid1.264",  "fname":"vid_from_q1.264"},
        "name2":{ "ip":"vid2.264",  "fname":"vid_from_q2.264"},
        "name3":{ "ip":"vid3.264",  "fname":"vid_from_q3.264"},
        "name4":{ "ip":"vid4.264",  "fname":"vid_from_q4.264"},
        "name5":{ "ip":"vid5.264",  "fname":"vid_from_q5.264"},
        "name6":{ "ip":"vid6.264",  "fname":"vid_from_q6.264"},
        "name7":{ "ip":"vid7.264",  "fname":"vid_from_q7.264"},
        "name8":{ "ip":"vid8.264",  "fname":"vid_from_q8.264"},
        "name9":{ "ip":"vid9.264",  "fname":"vid_from_q9.264"},
        "name10":{"ip":"vid10.264", "fname":"vid_from_q10.264"},
        "name11":{"ip":"vid11.264", "fname":"vid_from_q11.264"},
        "name12":{"ip":"vid12.264", "fname":"vid_from_q12.264"},
        "name13":{"ip":"vid13.264", "fname":"vid_from_q13.264"},
        "name14":{"ip":"vid14.264", "fname":"vid_from_q14.264"},
        "name15":{"ip":"vid15.264", "fname":"vid_from_q15.264"}
        }

for key in dict:
    ip = dict[key]["ip"]
    name = key
    q = queue.Queue()
    queues[name] = q
    cctv_reader = CCTVReader(q, ip, 8192)
    readers[name] = cctv_reader
    cctv_reader.start()

# Wait for all threads to end
for key in readers:
    readers[key].join()

# Save data for testing
for key in readers:
    fine_name = dict[key]["fname"]
    readers[key].save_q_to_file(fine_name)
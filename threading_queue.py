import queue
import threading

num_worker_threads = 4


def do_work(item):
    print(item)


def source():
    return range(100)


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        do_work(item)
        q.task_done()


q = queue.Queue()

threads = []

for i in range(num_worker_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)


for item in source():
    q.put(item)

# block until all tasks are done
q.join()

print('stopping workers!')

# stop workers
for i in range(num_worker_threads):
    q.put(None)

for t in threads:
    t.join()
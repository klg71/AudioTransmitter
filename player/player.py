import numpy as np
from time import sleep
# from sounddevice import CallbackStop
from sounddevice import OutputStream
from sounddevice import default
from sounddevice import query_devices
import socket
import argparse


dt = np.dtype(np.int16)
dt = dt.newbyteorder('<')


transmitted = []
next_file = False
filename = ""
bytebuffer = []
client_socket = None


def open_next_file():
    global bytebuffer
    global client_socket
    bytebuffer += list(client_socket.recv(64*1024))


def get_next_frame(filename):
    global bytebuffer
    global next_file
    bytes_frames = bytebuffer[:1024]
    bytebuffer = bytebuffer[1024:]
    print(len(bytebuffer))
    bytes_sliced = [bytes_frames[i*2:(i*2)+2] for i in range(0, int(len(bytes_frames)/2))]
    first = True
    left_sample = None
    right_sample = None
    frame_array = []
    for sample in bytes_sliced:
        if first:
            left_sample = np.frombuffer(bytes(sample), dt)[0]
            first = False

        else:
            right_sample = np.frombuffer(bytes(sample), dt)[0]
            first = True
            frame_array.append([left_sample, right_sample])

    for i in range(0, 256-len(frame_array)):
        frame_array.append([0, 0])
    frame = np.array(frame_array)
    return frame


def callback(outdata, frames, stream_time, status):
    global filename
    frame = get_next_frame(filename)
    if frame is not None:
        outdata[:] = frame


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Start audio playing client')
    parser.add_argument('--host', metavar='host', type=str, required=False,
                        help='Server IP')
    parser.add_argument('--port', metavar='port', type=int, default=8005, required=False,
                        help='Server Port (default: 8005)')
    parser.add_argument('--device', metavar='device', type=int, default=default.device[1], required=False,
                        help='Output device')
    parser.add_argument('--list', required=False, action='store_const', const=True,
                        help='List all audio devices')

    args = parser.parse_args()

    if not args.list:
        client_socket = socket.create_connection((args.host, args.port))
        open_next_file()
        # os.lseek(f, 44, os.SEEK_SET)
        sleep(2)
        stream = OutputStream(samplerate=44100.0, device=args.device, channels=2, dtype=dt, blocksize=256, callback=callback)
        stream.start()
        while True:
            if len(bytebuffer) < 30000:
                try:
                    open_next_file()
                except:
                    pass
            else:
                sleep(0.1)
    else:
        print(query_devices())

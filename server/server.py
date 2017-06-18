import numpy as np
from time import sleep
import ctypes
from ctypes import wintypes
import os
import msvcrt
import socket
import threading
import sys
import argparse

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000

OPEN_EXISTING = 3
OPEN_ALWAYS = 4

ACCESS_MODES = {
    "r": GENERIC_READ,
    "w": GENERIC_WRITE,
    "r+": (GENERIC_READ | GENERIC_WRITE)
}

OPEN_MODES = {
    "r": OPEN_EXISTING,
    "w": OPEN_ALWAYS,
    "r+": OPEN_ALWAYS,
}


dt = np.dtype(np.int16)
dt = dt.newbyteorder('<')


def open_file_nonblocking(filename, access):
    # Removes the b for binary access.
    internal_access = access.replace("b", "")
    access_mode = ACCESS_MODES[internal_access]
    open_mode = OPEN_MODES[internal_access]
    handle = wintypes.HANDLE(ctypes.windll.kernel32.CreateFileW(
        wintypes.LPWSTR(filename),
        wintypes.DWORD(access_mode),
        wintypes.DWORD(2 | 1),  # File share read and write
        ctypes.c_void_p(0),
        wintypes.DWORD(open_mode),
        wintypes.DWORD(0),
        wintypes.HANDLE(0)
    ))

    try:
        fd = msvcrt.open_osfhandle(handle.value, 0)
    except OverflowError as exc:
        # Python 3.X
        raise OSError("Failed to open file.") from None
        # Python 2
        # raise OSError("Failed to open file.")

    # return fd
    return os.fdopen(fd, access)


transmitted = []
next_file = False
filename = ""
bytebuffer = []
position_read = 0
alive = True
host = '0.0.0.0'
port = 8005
path = 'C:\\STREAM\\'


def get_int(file_name):
    return int(file_name[:-4])


def sort_files(files):
    return sorted(files, key=get_int)


def open_next_file():
    global transmitted
    global bytebuffer
    global filename
    global position_read
    global path
    while True:
        files = os.listdir(path)
        files = sort_files(files)
        if len(files) > 0:
            if files[-1] not in transmitted:
                transmitted.append(files[-1])
                stat = os.stat(os.path.join(path, files[-1]))
                if stat.st_size > 44:
                    sleep(2)
                    f = open_file_nonblocking(os.path.join(path, files[-1]), 'rb')
                    f.seek(44)
                    position_read = 0
                    readbuffer = f.read()
                    f.close()
                    readbuffer = list(readbuffer)
                    position_read += len(readbuffer)
                    bytebuffer += readbuffer
                    return
            if files[-1] == filename:
                stat = os.stat(os.path.join(path, files[-1]))
                if stat.st_size > (44+position_read+8*1024):
                    f = open_file_nonblocking(os.path.join(path, files[-1]), 'rb')
                    f.seek(44+position_read)
                    readbuffer = f.read()
                    f.close()
                    readbuffer = list(readbuffer)
                    position_read += len(readbuffer)
                    bytebuffer += readbuffer
                    return
            filename = files[-1]
        sleep(0.3)


def setup_server():
    global alive
    global host
    global port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)
    while alive:
        server_socket.setblocking(False)
        client_socket = None
        address = None
        while alive and client_socket is None:
            try:
                client_socket, address = server_socket.accept()
            except:
                pass
        if alive:
            server_socket.setblocking(True)
            client_socket.setblocking(True)
            print("new client: "+str(address))
        while alive:
            try:
                transmit_buffer(client_socket)
            except:
                print("disconnected: "+str(address))
                break


def transmit_buffer(client_socket):
    global bytebuffer
    global alive
    while alive:
        send_buffer = bytebuffer[:64*1024]
        bytebuffer = bytebuffer[64*1024:]
        if len(send_buffer) > 0:
            print(len(bytebuffer))
            client_socket.sendall(bytes(send_buffer))
        sleep(0.1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start audio sharing server.\n Reads data from C:\\STREAM\\')
    parser.add_argument('--host', metavar='host', type=str, default='0.0.0.0', required=False,
                        help='Host IP (default: 0.0.0.0)')
    parser.add_argument('--port', metavar='port', type=int, default=8005, required=False,
                        help='Host Port (default: 8005)')
    parser.add_argument('--path', metavar='path', type=str, default='C:\\STREAM\\', required=False,
                        help='Path for audio files (default: C:\\STREAM\\)')

    args = parser.parse_args()

    host = args.host
    port = args.port
    path = args.path

    t = None
    try:
        t = threading.Thread(target=setup_server, args=())
        t.start()

        open_next_file()
        sleep(1)
        while True:
            if len(bytebuffer) < 80000:
                try:
                    open_next_file()
                except:
                    pass
            sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        print("terminating")
        alive = False
        t.join()
        sys.exit()

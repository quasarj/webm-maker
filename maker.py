import win32gui
import os
import webbrowser
import subprocess
import progressbar

import hotpy
import uploader
import namer

VERSION = '1.1'

PID = None
name = None

def feed_file_to_handle_with_progress(filename, handle):
    chunk_size = 1024
    position = 0
    total = os.path.getsize(filename)

    widgets = [progressbar.Percentage(), ' ',
               progressbar.Bar(), ' ',
               progressbar.ETA(), ' ',
               progressbar.FileTransferSpeed()]
    bar = progressbar.ProgressBar(widgets=widgets, maxval=total)
    bar.start()

    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                handle.close()
                bar.finish()
                break
            handle.write(chunk)
            position += len(chunk)
            bar.update(position)



def cleanup(name):
    try:
        os.unlink('{}.avi'.format(name))
        os.unlink('{}.webm'.format(name))
    except FileNotFoundError:
        pass


def encode_video(name):
    p = subprocess.Popen('ffmpeg\\ffmpeg.exe '
            '-i - '
            '-c:v libvpx -b:v 10000k '
            '{}.webm'.format(name),
            bufsize=64,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.PIPE)
    print("Encoding...")
    feed_file_to_handle_with_progress('{}.avi'.format(name), p.stdin)
    p.wait()


def get_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def start_capture():
    global PID
    global name

    window = win32gui.GetForegroundWindow()
    title = get_title(window)

    name = namer.get_name()

    PID = subprocess.Popen('ffmpeg\\ffmpeg.exe -f gdigrab -i title="{}" '
                '-framerate 15 -vf "scale=\'iw/2\':-1" '
                '-c:v rawvideo -pix_fmt yuv420p '
                '{}.avi'.format(title, name),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.PIPE)

    print("\nCapturing has begun. Press Alt+F9 again to stop!\n")


def stop_capture():
    global PID
    global name

    # luckily, ffmpeg will accept a q on stdin as an exit command
    # lucky, becuase it's very hard to send a Ctrl+c to something in windows land
    PID.stdin.write(b'q')
    PID.stdin.flush()
    PID.wait()
    PID = None

    full_name = '{}.webm'.format(name)
    url = 'http://i.notabigtruck.com/i/tubes/{}'.format(full_name)

    print('Your url will be: {}'.format(url))

    encode_video(name)
    print('Uploading...')
    uploader.upload(full_name, full_name)

    cleanup(name)

    print('\n\n{}\n\n'.format(url))
    webbrowser.open(url)


def handle_f9():
    global PID

    if PID is None:
        start_capture()
    else:
        stop_capture()


def main():
    hotpy.register(handle_f9, 'F9', ['Alt'])
    hotpy.register(lambda: False, 'F9', ['Ctrl'])  # exit

    print("A Series of Tubes, v{}".format(VERSION))
    print("A simple webm maker")

    print("\nBrought to you by Quasar, Joseph, and The Cult of Done\n")

    print("Press Alt+F9 to start recording!")
    print("Press Ctrl+F9 to exit.\n\n")

    hotpy.listen()


if __name__ == '__main__':
    main()

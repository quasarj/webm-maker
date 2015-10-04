import sys
sys.path.insert(0, '.')  # Fix for config loading from py2exe

import win32gui
import os
import webbrowser
import subprocess
import progressbar
import argparse

import hotpy
import uploader
import namer

import config

VERSION = '1.3'

PID = None
name = None
args = None

def feed_file_to_handle_with_progress(filename, handle):
    chunk_size = 4096
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
    if config.cleanup:
        try:
            os.unlink('{}.avi'.format(name))
            os.unlink('{}.webm'.format(name))
        except FileNotFoundError:
            pass


def encode_video(name):
    command = ('ffmpeg\\ffmpeg.exe '
               '-i - '
               ' {} '
               ' {}.webm'.format(config.encode_parameters, name))

    if not args.debug:
        # suppress all output from ffmpeg
        output = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        output = {}

    p = subprocess.Popen(command,
        bufsize=64,
        stdin=subprocess.PIPE,
        **output)
    print("Encoding...")
    feed_file_to_handle_with_progress('{}.avi'.format(name), p.stdin)
    p.wait()


def get_title(hwnd):
    return win32gui.GetWindowText(hwnd)

def get_scale_setting():
    if args.full_size:
        return ''

    if config.half_size_capture or args.half_size:
        return '-vf "scale=\'iw/2\':-1" '
    else:
        return ''

def start_capture():
    global PID
    global name

    window = win32gui.GetForegroundWindow()
    title = get_title(window)

    if args.debug:
        print("Capture beginning, target window = {}".format(title))

    name = namer.get_name()

    if not args.debug:
        # suppress all output from ffmpeg
        output = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        output = {}

    PID = subprocess.Popen('ffmpeg\\ffmpeg.exe -f gdigrab -i title="{title}" '
                '-framerate 15 '
                '{scale} '
                '-c:v rawvideo -pix_fmt yuv420p '
                '{name}.avi'.format(title=title,
                                    name=name,
                                    scale=get_scale_setting()),
                stdin=subprocess.PIPE,
                **output)

    print("\nCapturing has begun. Press {} again to stop!\n".format(
         hotkey_printable_name(config.record_hotkey)))


def make_url(filename):
    return 'http://i.notabigtruck.com/i/tubes/{}'.format(filename)


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
    url = make_url(full_name)

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

def hotkey_printable_name(hotkey):
    key, *modifiers = hotkey

    # break out of outter list, if set
    if len(modifiers) > 0:
        modifiers = modifiers[0]

    return '+'.join(['+'.join(modifiers), key])


def exit():
    if args.debug:
        print("Exit hotkey pressed, exiting normally.")
    return False


def main():
    if args.debug:
        print("Values read from config file:")
        print("record_hotkey=", config.record_hotkey)
        print("exit_hotkey=", config.exit_hotkey)
        print("half_size_capture=", config.half_size_capture)
        print("encode_parameters=", config.encode_parameters)
        print("cleanup=", config.cleanup)
        print("\n\n")

    hotpy.register(handle_f9, *config.record_hotkey)
    hotpy.register(exit, *config.exit_hotkey)

    print("Press {} to start recording!".format(
         hotkey_printable_name(config.record_hotkey)))
    print("Press {} to exit.\n\n".format(
         hotkey_printable_name(config.exit_hotkey)))

    hotpy.listen()


def print_welcome_message():
    print("A Series of Tubes, v{}".format(VERSION))
    print("A simple webm maker")

    print("\nBrought to you by Quasar, Joseph, and The Cult of Done\n")


def parse_args():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('--half-size', action='store_const', const=bool,
                        help='capture at half size (supersedes config file)')
    parser.add_argument('--full-size', action='store_const', const=bool,
                        help='capture at full size (supersedes config file)')
    parser.add_argument('--debug', action='store_const', const=bool,
                        help='enable a very verbose debug mode')
    parser.add_argument("--upload", "-u",
            help="instead of running normally, "
                 "upload the given file to The Truck")
    args = parser.parse_args()


def upload_only():
    url = make_url(args.upload)
    print("Uploading to: {}".format(url))
    uploader.upload(args.upload, args.upload)
    webbrowser.open(url)


if __name__ == '__main__':
    print_welcome_message()
    parse_args()
    if args.upload:
        upload_only()
    else:
        main()

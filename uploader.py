import paramiko
import progressbar

import settings

def make_progress_callback():
    widgets = [progressbar.Percentage(), ' ',
               progressbar.Bar(), ' ',
               progressbar.ETA(), ' ',
               progressbar.FileTransferSpeed()]

    bar = progressbar.ProgressBar(widgets=widgets)

    def progress(current, total):
        nonlocal bar
        if bar is None:
            return

        bar.maxval = total

        if current == total:
            bar.finish()
            bar = None  # delete the bar instance to make sure we
                        # we don't call update() again
        else:
            bar.update(current)

    return progress


def upload(source_filename, dest_filename):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(settings.hostname,
                   username=settings.username,
                   password=settings.password)
    sftp = client.open_sftp()

    sftp.put(source_filename, 'tubes/' + dest_filename, make_progress_callback())

    # print("Complete, exiting")
    client.close()


if __name__ == '__main__':
    import sys
    upload(sys.argv[1], sys.argv[1])

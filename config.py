# This is the configuration file for the webm-maker.

# The hotkeys to listen for. Note that the key comes first, then the modifiers.
# Some more examples:
# record_hotkey = ['F9', ['Alt', 'Shift']]
record_hotkey = ['F9', ['Alt']]
exit_hotkey = ['F9', ['Ctrl']]

# Capture will be done at 1/2 scale if set to true. False will capture at full size.
# Half size is much easier on the system and results in half sized files, too :)
half_size_capture = True

# The actual parameters passed to ffmpeg for encoding.
# Only change these if you are feeling adventurous.
# Here are some other "default" quality settings I have tested:
# Low quality, small filesize
# encode_parameters = '-c:v libvpx -b:v 1M -crf 10'
# Medium quality
# encode_parameters = '-c:v libvpx -b:v 3M -crf 4'
# High quality
# encode_parameters = '-c:v libvpx -b:v 5M -crf 4'
# Very High quality
# encode_parameters = '-c:v libvpx -b:v 10M -crf 4'
# Ridiculous quality (untested, but I expect it'll make huge files)
# encode_parameters = '-c:v libvpx -b:v 50M -crf 4'
encode_parameters = '-c:v libvpx -b:v 10M -crf 4'

# If True, all local temporary files are deleted after upload
cleanup = True

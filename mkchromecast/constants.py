# This file is part of mkchromecast.

import enum
from typing import List


@enum.unique
class OpMode(enum.Enum):
    AUDIOCAST = enum.auto()
    DISCOVER = enum.auto()
    INPUT_FILE = enum.auto()
    RESET = enum.auto()
    SCREENCAST = enum.auto()
    SOURCE_URL = enum.auto()
    TRAY = enum.auto()
    VERSION = enum.auto()
    YOUTUBE = enum.auto()


# Formerly, "no96k", which was misleading because it implied that (for instance)
# 88200 was valid, which it is not.
MAX_48K_CODECS = {"ogg", "mp3"}
MAX_48K_SAMPLE_RATES = [22050, 32000, 44100, 48000]
ALL_SAMPLE_RATES = MAX_48K_SAMPLE_RATES + [88200, 96000, 176000, 192000]
QUANTIZED_SAMPLE_RATE_CODECS = ["mp3", "ogg", "aac", "opus", "wav", "flac"]

def sample_rates_for_codec(codec: str) -> List[int]:
    """Returns the appropriate sample rates for the given codec."""
    if codec in MAX_48K_CODECS:
        return MAX_48K_SAMPLE_RATES

    return ALL_SAMPLE_RATES


DARWIN_BACKENDS = ["node", "ffmpeg"]
LINUX_VIDEO_BACKENDS = ["node", "ffmpeg"]
LINUX_BACKENDS = ["ffmpeg", "parec"]
ALL_BACKENDS = ["node", "ffmpeg", "parec"]

def backend_options_for_platform(platform: str, video: bool = False):
    if platform == "Darwin":
        return DARWIN_BACKENDS

    if video:
        return LINUX_VIDEO_BACKENDS

    return LINUX_BACKENDS


DEFAULT_BITRATE = 192
CODECS_WITH_BITRATE = ["aac", "mp3", "ogg", "opus"]
# TODO(xsdg): Reverse how this is defined.
ALL_CODECS = QUANTIZED_SAMPLE_RATE_CODECS
NODE_CODEC = "mp3"


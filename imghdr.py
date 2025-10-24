"""
Local fallback for the removed Python stdlib 'imghdr' (Python 3.13+).
Used by python-telegram-bot to detect image types.
"""

import struct

def what(file, h=None):
    if h is None:
        with open(file, "rb") as f:
            h = f.read(32)

    if h.startswith(b"\xff\xd8"):
        return "jpeg"
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if h.startswith(b"BM"):
        return "bmp"
    if h.startswith(b"RIFF") and h[8:12] == b"WEBP":
        return "webp"
    if h[:4] == b"\x00\x00\x01\x00":
        return "ico"
    if h[:4] == b"II*\x00" or h[:4] == b"MM\x00*":
        return "tiff"
    return None

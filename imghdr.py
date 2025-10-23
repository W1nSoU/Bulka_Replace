"""Recognize image file formats based on their first few bytes."""

from os import PathLike
from collections.abc import Sequence


__all__ = ["what"]

#
# public interface
#

def what(file, h=None):
    """Recognize images by their file format.

    file -- a filename or a file-like object.
    h -- a file-like object which is rewinded to the beginning before being
         read from.
    """
    f = None
    location = None
    try:
        if h is None:
            if isinstance(file, (str, PathLike)):
                f = open(file, 'rb')
                h = f
            else:
                h = file
        try:
            location = h.tell()
        except (AttributeError, OSError):
            location = None
        h.seek(0)
        try:
            for tf in tests:
                res = tf(h.read(32), h)
                if res:
                    return res
        finally:
            if location is not None:
                h.seek(location)
    finally:
        if f:
            f.close()
    return None

#
# internal
#

tests = []

def test_jpeg(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'
    return None

tests.append(test_jpeg)

def test_png(h, f):
    if h.startswith(b'\211PNG\r\n\032\n'):
        return 'png'
    return None

tests.append(test_png)

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    return None

tests.append(test_gif)

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        return 'tiff'
    return None

tests.append(test_tiff)

def test_rgb(h, f):
    """SGI image library"""
    if h.startswith(b'\001\332'):
        return 'rgb'
    return None

tests.append(test_rgb)

def test_pbm(h, f):
    """PBM (portale bitmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'
    return None

tests.append(test_pbm)

def test_pgm(h, f):
    """PGM (portable graymap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'
    return None

tests.append(test_pgm)

def test_ppm(h, f):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'
    return None

tests.append(test_ppm)

def test_rast(h, f):
    """Sun raster file"""
    if h.startswith(b'\x59\xA6\x6A\x95'):
        return 'rast'
    return None

tests.append(test_rast)

def test_xbm(h, f):
    """X bitmap (X10 or X11)"""
    if h.startswith(b'#define '):
        return 'xbm'
    return None

tests.append(test_xbm)

def test_bmp(h, f):
    if h.startswith(b'BM'):
        return 'bmp'
    return None

tests.append(test_bmp)

def test_webp(h, f):
    if h.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'
    return None

tests.append(test_webp)

def test_exr(h, f):
    if h.startswith(b'\x76\x2f\x31\x01'):
        return 'exr'
    return None

tests.append(test_exr)

# AVIF and HEIF based on ISO/IEC 23008-12:2017
def test_avif(h, f):
    if h[4:12] == b'ftypavif':
        return 'avif'
    return None

tests.append(test_avif)

def test_heic(h, f):
    if h[4:12] == b'ftypheic':
        return 'heic'
    return None

tests.append(test_heic)

def test_heif(h, f):
    if h[4:12] == b'ftypheif':
        return 'heif'
    return None

tests.append(test_heif)

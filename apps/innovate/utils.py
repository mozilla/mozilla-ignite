import hashlib
import math
import os
import time

import Image

from django.core.files.storage import FileSystemStorage
from django.conf import settings

def get_partition_id(pk, chunk_size=1000):
    """
    Given a primary key and optionally the number of models that will get
    shared access to a directory, return an integer representing a directory
    name.
    """
    return int(math.ceil(pk / float(chunk_size)))


def safe_filename(filename):
    """Generate a safe filename for storage."""
    name, ext = os.path.splitext(filename)
    return "%s%s" % (hashlib.md5(name.encode('utf8')).hexdigest(), ext)


class ImageStorage(FileSystemStorage):

    format_extensions = {
        'PNG': 'png',
        'GIF': 'gif',
        'JPEG': 'jpg',
        'JPG': 'jpg',
    }

    def _save(self, name, content):
        name, ext = os.path.splitext(name)
        image = Image.open(content)
        if image.format not in self.format_extensions:
            raise Exception("Unknown image format: %s" % (image.format,))
        format = self.format_extensions[image.format]
        name = "%s%s.%s" % (name, str(time.time()), format)
        image.save(self.path(name), image.format)
        return name



import hashlib
import os
import time

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import SuspiciousOperation
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.encoding import smart_str

class CAStorageUtils():

    @staticmethod
    def hash_filename(filename, digestmod=hashlib.sha1,
                      chunk_size=UploadedFile.DEFAULT_CHUNK_SIZE):

        """
        Return the hash of the contents of a filename, using chunks.
            >>> import os.path as p
            >>> filename = p.join(p.abspath(p.dirname(__file__)), 'models.py')
            >>> hash_filename(filename)
            'da39a3ee5e6b4b0d3255bfef95601890afd80709'
        """

        fileobj = File(open(filename))
        try:
            return CAStorage.hash_chunks(fileobj.chunks(chunk_size=chunk_size))
        finally:
            fileobj.close()

    @staticmethod
    def hash_chunks(iterator, digestmod=hashlib.sha1):

        """
        Hash the contents of a string-yielding iterator.
            >>> import hashlib
            >>> digest = hashlib.sha1('abc').hexdigest()
            >>> strings = iter(['a', 'b', 'c'])
            >>> hash_chunks(strings, digestmod=hashlib.sha1) == digest
            True
        """

        digest = digestmod()
        for chunk in iterator:
            digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def shard(string, width, depth, rest_only=False):

        """
        Shard the given string by a width and depth. Returns a generator.
        A width and depth of 2 indicates that there should be 2 shards of length 2.
            >>> digest = '1f09d30c707d53f3d16c530dd73d70a6ce7596a9'
            >>> list(shard(digest, 2, 2))
            ['1f', '09', '1f09d30c707d53f3d16c530dd73d70a6ce7596a9']
        A width of 5 and depth of 1 will result in only one shard of length 5.
            >>> list(shard(digest, 5, 1))
            ['1f09d', '1f09d30c707d53f3d16c530dd73d70a6ce7596a9']
        A width of 1 and depth of 5 will give 5 shards of length 1.
            >>> list(shard(digest, 1, 5))
            ['1', 'f', '0', '9', 'd', '1f09d30c707d53f3d16c530dd73d70a6ce7596a9']
        If the `rest_only` parameter is true, only the remainder of the sharded
        string will be used as the last element:
            >>> list(shard(digest, 2, 2, rest_only=True))
            ['1f', '09', 'd30c707d53f3d16c530dd73d70a6ce7596a9']
        """

        for i in range(depth):
            yield string[(width * i):(width * (i + 1))]

        if rest_only:
            yield string[(width * depth):]
        else:
            yield string

    @staticmethod
    def rm_file_and_empty_parents(filename, root=None):
        """Delete a file, keep removing empty parent dirs up to `root`."""
        if root:
            root_stat = os.stat(root)

        os.unlink(filename)
        directory = os.path.dirname(filename)
        while not (root and os.path.samestat(root_stat, os.stat(directory))):
            if os.listdir(directory):
                break
            os.rmdir(directory)
            directory = os.path.dirname(directory)

class CAStorage():

    def __init__(self, location=None, sharding = (2,2)):
        self.location = location
        self.shard_width, self.shard_depth = sharding
        self.keep_extension = True

    def digest(self, content_iterator):
        """
        Create a digest using the contents of a file
        :param content: The path to a file
        :return: digest
        """
        # digest = CAStorageUtils.hash_chunks(content.chunks())
        digest = CAStorageUtils.hash_chunks(content_iterator)
        # content_iterator.seek(0)
        return digest

    def shard(self, hexdigest):
        return list(CAStorageUtils.shard(hexdigest, self.shard_width, self.shard_depth, rest_only=False))

    def path(self, hexdigest):
        shards = self.shard(hexdigest)

        try:
            path = safe_join(self.location, *shards)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." %
                                      ('/'.join(shards),))

        return smart_str(os.path.normpath(path))

    def delete(self, name, sure=False):
        if not sure:
            # Ignore automatic deletions; we don't know how many different
            # records point to one file.
            return

        path = name
        if os.path.sep not in path:
            path = self.path(name)
        CAStorageUtils.rm_file_and_empty_parents(path, root=self.location)

    def _save(self, name, f_path):

        f2 = open(f_path, 'r')
        content = f2.readlines()

        content_iterator = iter(f2.read(1024))
        digest = self.digest(content_iterator)
        if self.keep_extension:
            digest += os.path.splitext(name)[1]
        path = self.path(digest)
        if os.path.exists(path):
            return digest
        # return super(CAStorage, self)._save(digest, content)
        dir_path_idx = path.rindex('/')
        dir_path = (path[:dir_path_idx])
        try:
            os.makedirs(dir_path)
        except OSError:
            pass  # directory exists
        out_file = open(path, "w")
        out_file.writelines(content)
        out_file.close()


class Command(BaseCommand):
    help = 'Populates the database from the pacer system using a specified date range'
    # python manage.py checkcasecountsfromindexfile jsnetwork_project/media/pacer_bankruptcy_idx/

    def add_arguments(self, parser):
        # parser.add_argument('case_file_dir', type=str)
        pass

    def handle0(self, *args, **options):
        start = time.time()
        # initialization
        from django.conf import settings
        base_loc = os.path.join(settings.MEDIA_ROOT, 'bkcy_test')
        if not os.path.exists(base_loc):
            os.makedirs(base_loc)
        cs = CAStorage(location=base_loc)

        test_file = os.path.join(settings.MEDIA_ROOT, 'test_bankruptcy_party_insert copy.sql')
        # make digest
        # f = open(test_file ,"r")
        # f_iter = iter(f.read(1024))
        # digest = cs.digest(f_iter)
        # print(digest)
        # digest_shard = cs.shard(digest)
        # print(digest_shard)

        # test create file
        cs._save('template.txt', test_file)

    def handle(self, *args, **options):
        def _fetch_records():
            from pacerscraper.models import Ba

        # initialization
        from django.conf import settings
        base_loc = os.path.join(settings.MEDIA_ROOT, 'bkcy_test')
        if not os.path.exists(base_loc):
            os.makedirs(base_loc)
        cs = CAStorage(location=base_loc)




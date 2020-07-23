
import os, sys, argparse, tempfile, gzip

from boto.s3.key import Key
from io import open


def add_file(source_file, s3_key):
    """write a file to an s3 key"""
    if source_file.endswith(".js") or source_file.endswith(".css"):
        print("gzipping %s to %s" % (source_file, s3_key.key))
        gzip_to_key(source_file, s3_key)
    else:
        print("uploading %s to %s" % (source_file, s3_key.key))
        s3_key.set_contents_from_filename(source_file)


def gzip_to_key(source_file, key):
    tmp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".gz", delete=False)
    with open(source_file, 'rb') as f_in:
        with gzip.open(tmp_file.name, 'wb') as gz_out:
            gz_out.writelines(f_in)
    key.set_metadata('Content-Type', 'application/x-javascript' if source_file.endswith(".js") else 'text/css')
    key.set_metadata('Content-Encoding', 'gzip')
    key.set_contents_from_filename(tmp_file.name)
    os.unlink(tmp_file.name)  # clean up the temp file


def dir_to_bucket(src_directory, bucket):
    """recursively copy files from source directory to boto bucket"""
    for root, sub_folders, files in os.walk(src_directory):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, src_directory)
            # get S3 key for this file
            k = Key(bucket)
            k.key = rel_path
            add_file(abs_path, k)

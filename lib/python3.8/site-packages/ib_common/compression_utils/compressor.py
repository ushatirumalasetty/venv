from .abstract_compressor import AbstractCompressor
__author__ = 'vedavidh'


class Compressor(AbstractCompressor):
    def __init__(self, *args, **kwargs):
        super(Compressor, self).__init__(*args, **kwargs)

        from .zlib_compressor import ZlibCompressor
        self.handler = ZlibCompressor(*args, **kwargs)

    def compress_string(self, string_):
        return self.handler.compress_string(string_)

    def compress_file(self, file_name, output_file_name):
        return self.handler.compress_file(file_name, output_file_name)

    def decompress_string(self, compressed_string):
        return self.handler.decompress_string(compressed_string)

    def decompress_file(self, compressed_file_name, output_file_name):
        return self.handler.decompress_file(compressed_file_name, output_file_name)

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlunparse

import oss2

socket.setdefaulttimeout(20)

class OssMixin:
    
    def __init__(self, *args, **kwargs):
        # 从环境中读取
        ak = os.getenv('OSS_AK')
        sk = os.getenv('OSS_SK')
        assert ak and sk, 'OSS_AK or OSS_SK is not set'
        self.auth = oss2.Auth(ak, sk)
        oss2.defaults.multiget_threshold = 12 * 1024 * 1024
        oss2.defaults.multiget_part_size = 12 * 1024 * 1024
        oss2.defaults.multiget_num_threads = 10
        super().__init__(*args, **kwargs)
        
    def get_oss_info_from_url(self, url):
        url = urllib.parse.unquote(url)
        parsed_url = urlparse(url)
        # 获取endpoint
        endpoint = parsed_url.netloc.split('.', 1)[-1]
        # endpoint = endpoint.replace(".aliyuncs.com", "-internal.aliyuncs.com")
        # 获取bucket
        bucket = parsed_url.netloc.split('.', 1)[0]
        # 获取key，因为urlparse的path方法返回的路径以'/'开头，所以我们需要去掉开头的'/'
        key = parsed_url.path.lstrip('/')
        return endpoint, bucket, key
    
    def download_object(self, url, outfile=None):
        max_retries = 3
        retries = 0
        o = urlparse(url)
        if o.netloc.endswith('aliyuncs.com') and len(o.netloc.split('.')) == 4:
            p = o.netloc.split('.')
            # if not p[1].endswith('-internal'):
            #     p[1] += '-internal'
            url = urlunparse((o.scheme, '.'.join(p), o.path, o.params, o.query, o.fragment))
        while retries < max_retries:
            try:
                urllib.request.urlretrieve(url, filename=outfile)
            except urllib.error.HTTPError as e:
                raise f'{str(e)}, "url": {url}'

            except urllib.error.URLError as e:
                retries += 1
                time.sleep(10)
                if retries >= max_retries:
                    raise f'downloading "url": {url} time-out'
            else:
                return outfile

    def get_object_handle(self, url):
        try:
            endpoint, bucket, key = self.get_oss_info_from_url(url)
            bucket = oss2.Bucket(self.auth, endpoint, bucket, connect_timeout=60, enable_crc=False)
            h = bucket.get_object(key)
        except oss2.exceptions.NoSuchKey as e:
            raise f'{e.message}, "url": {url}'
        else:
            return h
        
    def is_file_larger_than_20mb(file_path):
        # 获取文件大小，单位为字节
        file_size = os.path.getsize(file_path)
        # 20MB 对应的字节数，1MB = 1024 * 1024 字节
        size_limit = 20 * 1024 * 1024
        # 判断文件大小是否大于 20MB
        return file_size > size_limit

    def get_object_file(self, url, outfile=None):
        try:
            if outfile is None:
                local_name = os.path.basename(key)
            else:
                local_name = outfile
            endpoint, bucket, key = self.get_oss_info_from_url(url)
            bucket = oss2.Bucket(self.auth, endpoint, bucket, connect_timeout=60, enable_crc=False)
            bucket.get_object_to_file(key, local_name)
            # oss2.resumable_download(bucket, key, local_name)
        except oss2.exceptions.NoSuchKey as e:
            raise f'{e.message}, "url": {url}'
        else:
            return outfile

    def file_exists(self, url):
        endpoint, bucket, key = self.get_oss_info_from_url(url)
        bucket = oss2.Bucket(self.auth, endpoint, bucket, connect_timeout=60, enable_crc=False)
        return bucket.object_exists(key)

    def post_object_file(self, url, file):
        endpoint, bucket, key = self.get_oss_info_from_url(url)
        bucket = oss2.Bucket(self.auth, endpoint, bucket, connect_timeout=60, enable_crc=False)
        # 指定允许覆盖已存在的文件
        headers = {'x-oss-forbid-overwrite': 'false'}
        if not OssMixin.is_file_larger_than_20mb(file):
            bucket.put_object_from_file(key, file, headers = headers)
        else:
            oss2.resumable_upload(bucket, key, file, headers = headers)
        return url
    
    def post_object(self, url, handle):
        endpoint, bucket, key = self.get_oss_info_from_url(url)
        bucket = oss2.Bucket(self.auth, endpoint, bucket, connect_timeout=60, enable_crc=False)
        bucket.put_object(key, handle)
        return url

    def list_objects(self, prefix, delimiter):
        result = []
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, delimiter=delimiter):
            result.append(obj.key)
        return result[1:]
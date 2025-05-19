# digital_campus/storage_backends.py
import os
from django.contrib.staticfiles.storage import ManifestFilesMixin
from storages.backends.s3boto3 import S3Boto3Storage


# ---- STATIC ----
class StaticStorage(ManifestFilesMixin, S3Boto3Storage):
    """
    Hashed static assets on S3 (collectstatic → manifest JSON + hashed filenames).
    """
    # Pull from your env var:
    bucket_name = os.environ["AWS_STATIC_BUCKET"]
    location    = "static"
    default_acl = None
    file_overwrite = True


# ---- MEDIA ----
class MediaStorage(S3Boto3Storage):
    """
    User-uploaded media on S3 (no hashing, preserve filenames).
    """
    bucket_name    = os.environ["AWS_MEDIA_BUCKET"]
    location       = "media"
    default_acl    = None
    file_overwrite = False


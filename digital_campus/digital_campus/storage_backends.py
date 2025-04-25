from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = None

class MediaStorage(S3Boto3Storage):
    bucket_name   = settings.AWS_STORAGE_BUCKET_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    default_acl   = None
    file_overwrite = False
    location      = 'media'    # so MEDIA_URL/media-path
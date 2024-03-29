"""Model to S3 Bucket mapping."""

from audio_api.aws.s3.models import RadioProgramFile
from audio_api.aws.settings import S3Buckets

S3_BUCKETS = {
    RadioProgramFile: S3Buckets.radio_programs,
}

import hashlib

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()


class UploadService:
    cloudinary.config(secure=True)

    @staticmethod
    def create_new_avatar(email: str, prefix: str):
        name = hashlib.sha256(email.encode()).hexdigest()[:12]
        return f"{prefix}/{name}"

    @staticmethod
    def upload(file, public_id):
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    @staticmethod
    def get_url_avatar(public_id, version):
        src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=version)
        return src_url

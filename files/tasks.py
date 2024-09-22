from celery import shared_task

from django.core.files.base import ContentFile

from .models import File

# Image processing stuff
from io import BytesIO
from PIL import Image

from core.utils import randomlongstr

import logging

logger = logging.getLogger("Django Starter Project")


@shared_task(name="process_thumbnails")
def process_thumbnails(app_file_id):

    app_file = File.objects.filter(id=app_file_id).first()

    if not app_file:
        return True

    logger.info("--> Processing image thumbnail")
    image = Image.open(app_file.file)
    logger.info("--> Original image opened")
    basewidth = 500  # Thumbnail size
    wpercent = basewidth / float(image.size[0])
    hsize = int((float(image.size[1]) * float(wpercent)))
    image.thumbnail((basewidth, hsize), Image.Resampling.LANCZOS)
    logger.info("--> Thumbnail generated")

    # Save the thumbnail
    temp_handle = BytesIO()
    image.save(temp_handle, format=image.format)
    app_file.thumbnail.save(
        "thumb_" + randomlongstr() + app_file.file_extension,
        ContentFile(temp_handle.getvalue()),
    )

    logger.info("--> Thumbnail saved")
    logger.info("--> Thumbnail generated in worker")

    logger.info("--> Processing image micro thumbnail")
    image = Image.open(app_file.file)
    logger.info("--> Original image opened")
    basewidth = 200  # Thumbnail size
    wpercent = basewidth / float(image.size[0])
    hsize = int((float(image.size[1]) * float(wpercent)))
    image.thumbnail((basewidth, hsize), Image.Resampling.LANCZOS)
    logger.info("--> Micro thumbnail generated")

    # Save the thumbnail
    temp_handle = BytesIO()
    image.save(temp_handle, format=image.format)
    app_file.micro_thumbnail.save(
        "micro_" + randomlongstr() + app_file.file_extension,
        ContentFile(temp_handle.getvalue()),
    )

    logger.info("--> Micro thumbnail saved")
    logger.info("--> Micro thumbnail generated in worker")

    return True


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(
        (
            (img_width - crop_width) // 2,
            (img_height - crop_height) // 2,
            (img_width + crop_width) // 2,
            (img_height + crop_height) // 2,
        )
    )

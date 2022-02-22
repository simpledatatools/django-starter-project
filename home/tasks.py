from celery import shared_task

# Utils
from home.utils import *

# Models
from home.models import *
from accounts.models import *


@shared_task(name="Create a log")
def add_log(log_message):
    print(log_message)
    return True



# ------------------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------------------

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

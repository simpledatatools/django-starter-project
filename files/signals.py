from django.dispatch import receiver
from django.db.models.signals import post_save
from core.utils import randomstr

@receiver(post_save, sender=AppFile)
def init_app_file(sender, instance, **kwargs):

    if kwargs['created']:

        # Create the display_id
        instance.display_id = randomstr()
        instance.save()
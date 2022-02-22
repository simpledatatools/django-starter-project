from django.db.models.signals import pre_save
from .models import *
from core.utils import randomstr

def initWorkspace(sender, instance, **kwargs):
    workspace = instance
    # On init, add the other ids
    if workspace.workspace_id == None:
        workspace.workspace_id = randomstr()
    if workspace.public_key == None:
        workspace.public_key = publickey()
pre_save.connect(initWorkspace, sender=Workspace)
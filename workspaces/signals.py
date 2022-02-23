from django.db.models.signals import post_save, pre_save
from .models import *
from core.utils import randomstr

# Add a workspace_id if it does not exist (this will only happen only pre-initial save)
# Ids are returned in the api
def initWorkspace(sender, instance, **kwargs):
    workspace = instance
    if workspace.workspace_id == None:
        workspace.workspace_id = randomstr()
pre_save.connect(initWorkspace, sender=Workspace)

# Create a WorkspaceUser after the initial save of a workspace
def initWorkspaceUser(sender, instance, **kwargs):

    if kwargs['created']:

        workspace = instance
        workspace_user = WorkspaceUser.objects.create(
            workspace=workspace,
            user=user,
            role='admin' # Users creating are admins by default
        )

post_save.connect(initWorkspaceUser, sender=Workspace)

def initTag(sender, instance, **kwargs):
    tag = instance
    # On init, add the other ids
    if tag.tag_id == None:
        tag.tag_id = randomstr()
pre_save.connect(initTag, sender=Tag)
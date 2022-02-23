from documents.models import *

def check_workspace_permissions(user, workspace_id, roles):

    response = {}
    workspace = Workspace.objects.filter(workspace_id=workspace_id, status='active').first()
    if workspace:
        # Confirm the user has access
        workspace_user = WorkspaceUser.objects.filter(
            workspace=workspace, 
            user=user, 
            status='active',
            role__in=roles,
        ).first()
        
        if workspace_user:
            response['workspace'] = workspace
            return response
        else: 
            response['workspace'] = None
            response['message'] = 'Permission denied'
            return response
    else: 
        response['workspace'] = None
        response['message'] = "Workspace not found"
        return response
OWNER_PERMISSIONS = ['challenges.%s_submission' % v for v in ['edit', 'delete']]

class SubmissionBackend(object):
    """Provide custom permission logic for submissions."""
    
    supports_object_permissions = True
    supports_anonymous_user = True
    
    def authenticate(self):
        """This backend doesn't provide any authentication functionality."""
        return None
    
    def has_perm(self, user_obj, perm, obj=None):
        if perm in OWNER_PERMISSIONS:
            # Owners can edit and delete their own submissions
            if obj is not None and user_obj == obj.created_by.user:
                return True
        return False

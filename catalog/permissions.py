from rest_framework import permissions
from .models import Project


class IsProjectOwnerOrAdmin(permissions.BasePermission):
  """Custom permission class to enforce Business Rule 3 (Anti-cheat):

  - Commercials can only view, create, or modify assets/projects they own.
  - Admins (staff/superuser) have full access to everything.
  """

  def has_permission(self, request, view) -> bool:
    # Ensure the user is authenticated
    if not request.user or not request.user.is_authenticated:
      return False

    # Admins have global access
    if request.user.is_staff or request.user.is_superuser:
      return True

    # For safe methods (GET, HEAD, OPTIONS), allow access
    # (Filtering by role is handled in the ViewSet's get_queryset)
    if request.method in permissions.SAFE_METHODS:
      return True

    # For creation (POST), if an asset is being created, check project ownership
    project_id = request.data.get('project')
    if project_id:
      try:
        project = Project.objects.get(pk=project_id) #Check if the user requesting for the action is the owner
        return project.owner == request.user
      except Project.DoesNotExist:
        return False

    return True

  def has_object_permission(self, request, view, obj) -> bool:
    # Admins have full access to any object
    if request.user.is_staff or request.user.is_superuser:
      return True

    # Check if the object is a Project or an Asset and check which is the related project
    project = obj if hasattr(obj, 'owner') else getattr(obj, 'project', None)

    # Verify if the current user is the owner of the project
    if project:
      return project.owner == request.user

    return False
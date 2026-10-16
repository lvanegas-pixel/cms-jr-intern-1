from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from .models import Asset, Project
from .permissions import IsProjectOwnerOrAdmin
from .serializers import AssetSerializer, ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
  """ViewSet for managing Projects.

  - Rule 2 (Scoping by role): Commercials only see their own projects.
  Admins see everything.
  """

  serializer_class = ProjectSerializer
  permission_classes = [IsProjectOwnerOrAdmin]

  # Añadimos los backends de filtrado y búsqueda aquí
  filter_backends = [DjangoFilterBackend, filters.SearchFilter]
  filterset_fields = ['owner']  # Permite filtrar por dueño: ?owner=<id>
  search_fields = ['name']  # Permite buscar por texto: ?search=<texto>

  def get_queryset(self):
    user = self.request.user
    # Admins see all projects
    if user.is_staff or user.is_superuser:
      return Project.objects.all()
    # Commercials only see projects they own
    return Project.objects.filter(owner=user)

  def perform_create(self, serializer):
    # Automatically assign the logged-in user as the owner of the project
    serializer.save(owner=self.request.user)


class AssetViewSet(viewsets.ModelViewSet):
  """ViewSet for managing Assets.

  - Rule 2 (Scoping by role): Commercials only see assets belonging to their
  projects.
  - Rule 3 (Anti-cheat): Protected by IsProjectOwnerOrAdmin permission class.
  """

  serializer_class = AssetSerializer
  permission_classes = [IsProjectOwnerOrAdmin]

  # Añadimos los backends de filtrado y búsqueda también aquí
  filter_backends = [DjangoFilterBackend, filters.SearchFilter]
  filterset_fields = [
    'project',
    'asset_type',
    'is_public',
  ]  # Filtrar por tipo, proyecto o si es público
  search_fields = ['name']  # Permite buscar assets por nombre: ?search=<texto>

  def get_queryset(self):
    user = self.request.user
    # Admins see all assets
    if user.is_staff or user.is_superuser:
      return Asset.objects.all()
    # Commercials only see assets belonging to projects they own
    return Asset.objects.filter(project__owner=user)
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Asset, Project



class CatalogApiTests(APITestCase):
  """Automated test suite for CMS Jr.

  catalog API:
  - Verifies Asset CRUD operations.
  - Verifies Rule 1 (maximum one MODEL_3D per project).
  - Verifies Rule 2 (scoping by role: commercial sees only own projects, admin sees all).
  - Verifies Rule 3 / Permissions (commercials cannot modify others' projects).
  """

  def setUp(self):
    # 1. Create commercial users and an admin user
    self.user1 = User.objects.create_user(
        username='commercial1', password='password123'
    )
    self.user2 = User.objects.create_user(
        username='commercial2', password='password123'
    )
    self.admin_user = User.objects.create_superuser(
        username='adminuser', password='password123'
    )

    # 2. Create projects owned by different users
    self.project1 = Project.objects.create(
        name='Project Alpha', owner=self.user1
    )
    self.project2 = Project.objects.create(
        name='Project Beta', owner=self.user2
    )

    # 3. Define endpoints
    self.assets_url = reverse('asset-list')
    self.projects_url = reverse('project-list')

  def test_asset_crud_operations(self):
    """Ensure a user can create, retrieve, and list assets for their project."""
    self.client.force_authenticate(user=self.user1)

    # Create an IMAGE asset
    data = {
        'project': self.project1.id,
        'name': 'Banner Image',
        'asset_type': 'IMAGE',
        'is_public': True,
    }
    response = self.client.post(self.assets_url, data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    asset_id = response.data['id']

    # Retrieve the specific asset detail
    detail_url = reverse('asset-detail', kwargs={'pk': asset_id})
    response_detail = self.client.get(detail_url)
    self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
    self.assertEqual(response_detail.data['name'], 'Banner Image')

    # List assets
    response_list = self.client.get(self.assets_url)
    self.assertEqual(response_list.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response_list.data), 1)

  def test_rule_1_max_one_3d_model_per_project(self):
    """Ensure that adding a second MODEL_3D asset to the same project is blocked."""
    self.client.force_authenticate(user=self.user1)

    # First MODEL_3D asset should succeed
    data_first = {
        'project': self.project1.id,
        'name': 'Statue 3D',
        'asset_type': 'MODEL_3D',
        'is_public': True,
    }
    response_first = self.client.post(self.assets_url, data_first)
    self.assertEqual(response_first.status_code, status.HTTP_201_CREATED)

    # Second MODEL_3D asset for the same project should fail validation (Rule 1)
    data_second = {
        'project': self.project1.id,
        'name': 'Another Statue 3D',
        'asset_type': 'MODEL_3D',
        'is_public': False,
    }
    response_second = self.client.post(self.assets_url, data_second)
    self.assertEqual(response_second.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify that the serializer intercepts the business rule and rejects the request with
        # a 400 Bad Request error.

  def test_rule_2_commercial_scoping(self):
    """Ensure commercial users see only their projects, while admins see all projects."""
    # Authenticate as commercial1
    self.client.force_authenticate(user=self.user1)
    response_c1 = self.client.get(self.projects_url)
    self.assertEqual(response_c1.status_code, status.HTTP_200_OK)

    # commercial1 should only see project1 (Alpha), not project2 (Beta)
    project_ids_c1 = [p['id'] for p in response_c1.data]
    self.assertIn(self.project1.id, project_ids_c1)
    self.assertNotIn(self.project2.id, project_ids_c1)

    # Authenticate as admin user
    self.client.force_authenticate(user=self.admin_user)
    response_admin = self.client.get(self.projects_url)
    self.assertEqual(response_admin.status_code, status.HTTP_200_OK)

    # Admin should see both projects
    project_ids_admin = [p['id'] for p in response_admin.data]
    self.assertIn(self.project1.id, project_ids_admin)
    self.assertIn(self.project2.id, project_ids_admin)

  def test_rule_3_anti_cheat_permission(self):
    """Ensure commercial2 cannot modify or create assets in commercial1's project."""
    self.client.force_authenticate(user=self.user2)

    data = {
        'project': self.project1.id,
        'name': 'Unauthorized Asset',
        'asset_type': 'IMAGE',
        'is_public': True,
    }
    response = self.client.post(self.assets_url, data)
    self.assertIn(
        response.status_code,
        [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST],
    )
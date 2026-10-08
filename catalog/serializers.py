from rest_framework import serializers
from .models import Asset, Project

# DRF (Django REST Framework)

class AssetSerializer(serializers.ModelSerializer):
  """Serializer for Asset model handling business logic and validations."""

  class Meta:
    model = Asset
    fields = ['id', 'project', 'name', 'asset_type', 'is_public']

  def validate(self, attrs):
    """Business Rule 1: A project can only have ONE MODEL_3D asset.

    If someone tries to create/update a second MODEL_3D in the same project,
    raise a validation error.
    """
    # We obtain the project and the type of asset being saved.
    project = attrs.get('project')
    asset_type = attrs.get('asset_type')

    # If the type we are trying to save is a MODEL_3D...
    if asset_type == 'MODEL_3D':
      # We check whether an asset of type MODEL_3D already exists in this project.
      existing_3d_model = Asset.objects.filter(
          project=project, asset_type='MODEL_3D'
      )

      # If we are updating an existing asset, we must exclude it from the check.
      if self.instance:
        existing_3d_model = existing_3d_model.exclude(pk=self.instance.pk)

      if existing_3d_model.exists():
        raise serializers.ValidationError({
            'asset_type': (
                'This project already has a MODEL_3D asset. Only one is'
                'allowed.'
            )
        })

    return attrs


class ProjectSerializer(serializers.ModelSerializer):
  """Serializer for Project model."""

  # Optional: we can include the related assets if we want to see them in the API.
  assets = AssetSerializer(many=True, read_only=True)

  class Meta:
    model = Project
    fields = ['id', 'name', 'owner', 'created_at', 'assets']
    read_only_fields = ['owner', 'created_at']  # The owner is automatically assigned.
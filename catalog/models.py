from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
  """Represents a project in the CMS catalog."""

  name = models.CharField(max_length=255, unique=True) #The project name (required and minimum of 3 characters).
  owner = models.ForeignKey( #The sales representative or user responsible for that project.
      User,
      on_delete=models.CASCADE, #This means that if the owner user is deleted from the database, all their associated projects will be automatically deleted.
      related_name='projects'
  )
  created_at = models.DateTimeField(auto_now_add=True) #Django automatically records and saves the date and time.

  def __str__(self) -> str: #Makes Django display the project name.
    return self.name


class Asset(models.Model): #The Content Element
  """Represents a content asset inside a project (e.g., 3D model, image, video)."""

  ASSET_TYPES = [
      ('MODEL_3D', 'Model 3D'),
      ('IMAGE', 'Image'),
      ('VIDEO', 'Video'),
  ]

  project = models.ForeignKey(
      Project,
      on_delete=models.CASCADE,
      related_name='assets' #So that you can write `project.assets.all()` to get all the assets belonging to that project.
  )
  name = models.CharField(max_length=255)
  asset_type = models.CharField(max_length=20, choices=ASSET_TYPES) #You have to write the type of product you want to create and if you don't write it correctly an error will appear
  is_public = models.BooleanField(default=False)

  def __str__(self) -> str:
    return f'{self.name} ({self.asset_type})'
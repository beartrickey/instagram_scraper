import os, urllib

from django.core.files import File
from django.db import models


# Create your models here.
class Job(models.Model):

	tag = models.ForeignKey(
		to="pixlee_app.Tag",
		related_name="jobs",
	)
	
	from_date = models.DateField()
	to_date = models.DateField()
	
	image_count = models.IntegerField(default=0)
	checked_pages = models.IntegerField(default=0)
	last_max_tag_id = models.CharField(max_length=100, null=True, blank=True)
	last_modified_datetime = models.DateTimeField(auto_now=True, null=True, blank=True)

	job_start_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	job_end_datetime = models.DateTimeField(null=True, blank=True)


class Tag(models.Model):
	
	name = models.CharField(max_length=50)


class InstagramContent(models.Model):
	
	tag_date = models.DateField()
	tag = models.ForeignKey(
		to="pixlee_app.Tag",
		related_name="instagram_content",
	)
	instagram_id = models.CharField(max_length=100)
	image_url = models.URLField()
	image_file = models.ImageField(upload_to='images', null=True, blank=True)

	def get_remote_image(self):

		if self.image_url and not self.image_file:
			result = urllib.urlretrieve(self.image_url)
			self.image_file.save(
				os.path.basename(self.image_url),
				File(open(result[0]))
			)
			self.save()
	

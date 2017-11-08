from django.db import models
from django.utils import timezone

from summarymodule.models import News


class Tags(models.Model):
	tag_name = models.CharField(max_length=200)
	create_date = models.DateTimeField(default=timezone.now, blank=True)

	def __str__(self):
		return self.tag_name

	class Meta:
		db_table = "Tags"


class NewsTags(models.Model):
	id_tags = models.ForeignKey(Tags, on_delete=models.CASCADE)
	id_news = models.ForeignKey(News, on_delete=models.CASCADE)
	create_date = models.DateTimeField(default=timezone.now, blank=True)

	class Meta:
		db_table = 'NewsTags'
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class BlogArticles(models.Model):
    blog_title = models.CharField(max_length=120)
    blog_description = models.CharField(max_length=200)
    blog_text = models.TextField()
    blog_image = models.ImageField(upload_to='image/%Y/%m/%d', default='none/no-img.jpg',
                                   null=True, blank=True,
                                   height_field='height_field',
                                   width_field='width_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    vote_up = models.IntegerField(default=0)
    vote_down = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    visible = models.BooleanField(default=True)
    create_date = models.DateTimeField(default=timezone.now, blank=True)

    class Meta():
        db_table = 'BlogArticles'


class UserBlogs(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_blog = models.ForeignKey(BlogArticles, on_delete=models.CASCADE)
    vote = models.IntegerField()  # 1 = userul a votat pozitiv, -1 = userul a votat negativ, 0 = userul si-a retras votul
    last_date = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        db_table = 'UserBlogs'

from django.db import models, connection
from django.utils import timezone
from django.contrib.auth.models import User


class News(models.Model):
    article_title = models.CharField(max_length=100)
    article_text = models.TextField()
    article_description = models.TextField()
    article_url = models.CharField(max_length=250)
    article_date = models.DateTimeField()
    article_img_href = models.CharField(max_length=250, default='')
    vote_up = models.IntegerField(default=0)
    vote_down = models.IntegerField(default=0)
    create_date = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return self.article_title

    class Meta:
        db_table = 'News'


class UserNews(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_news = models.ForeignKey(News, on_delete=models.CASCADE)
    vote = models.IntegerField() # 1 = userul a votat pozitiv, -1 = userul a votat negativ, 0 = userul si-a retras votul
    last_date = models.DateTimeField(default=timezone.now, blank=True)


    class Meta:
        db_table = 'UserNews'


class ProcedureDuplicates():

    def solve_duplicates(self):
        cursor = connection.cursor()
        ret = cursor.callproc("delete_duplicates")# calls PROCEDURE named LOG_MESSAGE which resides in MY_UTIL Package
        cursor.close()
        return ret
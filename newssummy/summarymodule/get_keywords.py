#noinspection PyUnresolvedReferences
#import rake.rake as rake
import operator
from .models import News
from nltk.corpus import stopwords as sw
#noinspection PyUnresolvedReferences
# import RAKE
from datetime import datetime, timedelta
# from rake_nltk import Rake
import math

def get_keywords():
    stopwords = sw.words('english')

    # rake_object = rake.Rake("C:\\WORK\\Projects\\Python\\Django\\newssummy\\summarymodule\\SmartStoplist.txt", 5, 3, 4)
    #
    # #pentru citirea din fisiere folosind exemplul din librarie
    # # sample_file = open("C:/WORK/Projects/Python/Django/myenv/Lib/site-packages/rake/data/docs/fao_test/w2167e.txt", 'r')
    # # text = sample_file.read()
    #
    text = ''
    news = News.objects.filter(article_date__gte=datetime.now()-timedelta(days=7))
    for article in news:
        text += article.article_title + article.article_text + article.article_description

    # # print(text[:1500])
    # # text.replace('\n', '')
    # # print(text[:1500])
    # # keywords = rake_object.run(text)
    # # print("Keywords ", keywords)
    #
    # rake = Rake()
    # rake.extract_keywords_from_text(text)
    # keywords = rake.get_ranked_phrases()[:3]
    # #keywords = rake.run(text)[:3]
    # keywd = []
    # for k in keywords:
    #     keywd.append(k.capitalize())
    # return keywd

    def tf(word, blob):
        return blob.words.count(word) / len(blob.words)

    def n_containing(word, bloblist):
        return sum(1 for blob in bloblist if word in blob.words)

    def idf(word, bloblist):
        return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

    def tfidf(word, blob, bloblist):
        return tf(word, blob) * idf(word, bloblist)
    #
    # for i, blob in enumerate(bloblist):
    #     print("Top words in document {}".format(i + 1))
    #     scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
    #     sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    #     for word, score in sorted_words[:3]:
    #         print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
    #
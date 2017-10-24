import math
from nltk.corpus import stopwords
from nltk import data, WordNetLemmatizer, Counter, word_tokenize
from .models import News


def get_keywords():
    news = News.objects.all()
    news_text = []
    for article in news:
        news_text.append(article.article_text)

    tokens = []
    tfidf, tf = {}, {}

    for i in range(len(news_text)):
        tokens = word_tokenize(news_text[i])

        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

        v_stopwords = stopwords.words('english')
        tokens = [token for token in tokens if token not in v_stopwords]
        counter_list = []

        for key, value in Counter(tokens).items():
            counter_list.append((key,value))

        tf[i] = counter_list


        # for i in range(len(news_text)):
        #     for key, value in tf[i].items():
        #         print(value)
    print(range(len(tf)))
    print(tf[0][0][0],tf[0][0][1])
    print(tf[0][41][0], tf[0][41][1])
    idf = []
    print(len(idf))

    for i in range(len(news_text)):
        for t in range(len(tf[i])):
            print(len(tf[i]))
            print(t)
            print(i)
            print(tf[0][t][1])
            idf.append(math.log(len(news_text) / len([doc_index
                                                      for doc_index in range(len(tf))
                                                      if tf[doc_index][t][1] > 0])))

    print(idf)
    for curr_doc_index in range(len(news_text)):
        for t in range(len(tokens)):
            tfidf[t] = tf[curr_doc_index][t] * idf[t]

    print('tf este: {}'.format(tf[1]))

    terms_sorted_tfidf_desc = sorted(tfidf.items(), key=lambda x: -x[1])
    terms, scores = zip(*terms_sorted_tfidf_desc)
    keywords = terms[:5]
    print(keywords)

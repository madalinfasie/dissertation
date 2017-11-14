import nltk
from datetime import datetime, timedelta
from nltk.collocations import *
from nltk.tokenize import word_tokenize


def get_tags(text):
    stopwords = nltk.corpus.stopwords.words('english')

    # news_days_range = 30
    # news_article_text = News.objects.filter(article_date__gte=datetime.now()-timedelta(days=news_days_range)).values('article_text')

    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()

    finder_b = BigramCollocationFinder.from_words(word_tokenize(text))
    finder_t = TrigramCollocationFinder.from_words(word_tokenize(text))
    
    finder_b.apply_freq_filter(3)
    finder_t.apply_freq_filter(2)

    finder_b.apply_word_filter(lambda w: len(w) < 3 or w.lower() in stopwords)
    finder_t.apply_word_filter(lambda w: len(w) < 3 or w.lower() in stopwords)
    
    best_bigrams = finder_b.score_ngrams(bigram_measures.pmi)
    best_trigrams = finder_t.score_ngrams(trigram_measures.pmi)

    best_bigrams = best_bigrams[:15]
    best_trigrams = best_trigrams[:15]

    best_tags = best_bigrams + best_trigrams
    best_tags.sort(key=lambda x: -x[1])

    tags_list = []
    for pair in best_tags:
        if len(pair[0]) == 3:
            tags_list.append((pair[0][0] + " " + pair[0][1] + " " + pair[0][2], pair[1]))
        else:
            tags_list.append((pair[0][0] + " " + pair[0][1], pair[1]))

    return tags_list
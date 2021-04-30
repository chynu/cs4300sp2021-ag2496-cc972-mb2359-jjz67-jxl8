import numpy as np
import pickle
import gensim
import gensim.corpora as corpora
import os
import spacy
import unidecode as ud
import re
singernlp = spacy.load("en_core_web_trf", disable=['parser', 'ner'])


def ling_similarity(input_string):
    input_vec = turn_input_str_into_vec(input_string, 0.7)
    return get_artist_probs(topic_matrix, input_vec)


def turn_input_str_into_vec(input_str, threshold):
    input_bow = id2word.doc2bow(super_tokenize(input_str, singernlp, stop_words=stop_words))
    input_topics = lda_model.get_document_topics(input_bow, minimum_probability=threshold)
    return vectorize_topic_list(input_topics)


def vectorize_topic_list(input_topic_list):
    t_vec = np.zeros(num_lda_topics)
    if len(input_topic_list) > 0:
        t_vec[np.array(input_topic_list).T.astype(int)[0]] = np.array(input_topic_list).T[1]
    return t_vec


def get_artist_probs(t_mat, input_vec):
    return np.dot(t_mat, input_vec.T).T


def super_tokenize(input_string, nlp_tool, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV', 'PROPN', 'INTJ'],
                   stop_words=[]):
    """
    Creates a list of tokens that are lemmatized, unicode-friendly, and stopword-free.
    Takes in a string and returns a list of strings.
    """
    # Cleaned and lowercase-ized
    nlp = nlp_tool(clean(input_string))
    return [token.lemma_ for token in nlp
            if (token.pos_ in allowed_postags and
                (token.lower_ not in stop_words and token.lemma_ not in stop_words))]


def clean(input_string, cap_code=-1):
    """
    Takes in string, returns a unicode-friendly and stripped version of the string.
    """
    cleaned_str = ud.unidecode(input_string).lower() if cap_code == -1 else ud.unidecode(input_string).upper()

    rpl = [(r'(^\s+)|(\s+$)|(\b\')|(\'\b)|(\b\")|(\"b)', ''),  # whitespace at beg/end of string
           (r'(\s+)|([\n|\r|\t|\0]+)', ' ')]
    for p, r in rpl:
        cleaned_str = re.sub(p, r, cleaned_str)
    return cleaned_str


def unpickle(filename):
    return pickle.load(open(os.path.join(os.path.dirname(__file__), "../../pickles/" + filename), "rb"))


# ===== LOAD VARIABLES ===== #
lda_model = unpickle("draft_lda_model.pk")
tokenized_reviews = unpickle("draft_tokenized_reviews.pk")
topic_matrix = unpickle("draft_topic_matrix.pk")  # shape: (num artists) x (num topics)
count_vectorizer = unpickle("pf_cvec.pk")
stop_words = unpickle("stop_words.pk")
lda_vocab = singernlp(" ".join(count_vectorizer.get_feature_names()))
id2word = corpora.Dictionary(tokenized_reviews)
num_lda_topics = topic_matrix.shape[1]
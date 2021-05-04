from . import *
from app.irsystem.models.search import *

import pandas as pd
import numpy as np
import ssl
import requests
import json

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"

ssl._create_default_https_context = ssl._create_unverified_context

tf_idf = pd.read_csv("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/data/processed/tfidf_mat_compressed.csv")
artist_details = pd.read_csv("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/removed_dups_new.csv")
jaccard = pd.read_csv("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/data/processed/jaccard.csv",index_col=[0]).to_numpy()

reviews = json.loads(requests.get("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/data/raw/ratings.json").text)

artist_names = tf_idf.values[:,0]
artist_name_to_index = {artist_names[i]: i for i in range(len(artist_names))}
matrix = tf_idf.to_numpy()[:,1:]

def get_artist_rating(artist_name):
    """ Returns rating of [artist_name], 'not found' if rating DNE.

    Parameters: {artist_name: String}
    Returns: Integer | String
    """
    try:
        return reviews[artist_name]
    except:
        return 'not found'

def get_artist_id(artist_name):
    """ Returns id of [artist_name]'s profile.
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        return artist_details['Artist ID'][artist_name_to_index[artist_name]]
    except:
        return "no id"
    
def get_artist_follower_count(artist_name):
    """ Returns follower count of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: String
    """
    return artist_details['followers'][artist_name_to_index[artist_name]]

def get_artist_description(artist_name):
    """ Returns description of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        followers = get_artist_follower_count(artist_name)
        return artist_name + " has " + str(followers) + " followers on Spotify."
    except:
        return "Couldn't find additional details on " + artist_name + ". "

def get_artist_genres(artist_name):
    """ Returns the genres of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: List
    """
    genres = artist_details['genres'][artist_name_to_index[artist_name]]
    return genres.translate(str.maketrans('','','[]\'')).split(', ')

def get_artist_photo(artist_name):
    """ Returns url of [artist_name]'s photo.
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        return artist_details['Image URL'][artist_name_to_index[artist_name]]
    except:
        return "https://www.pngitem.com/pimgs/m/148-1487614_spotify-logo-small-spotify-logo-transparent-hd-png.png"

def rocchio_update(query, query_obj, input_doc_mat=matrix, \
        artist_name_to_index=artist_name_to_index,a=.3, b=.3, c=.3):
    """ Returns a vector representing the modified query vector.

    Note:
        Be sure to handle the cases where relevant and irrelevant are empty lists.
        
    Params: {query: Int (index of artist being queried for),
             query_obj: Dict (storing the names of relevant and irrelevant artists for query),
             input_doc_mat: Numpy Array,
             artist_name_to_index: Dict,
             a,b,c: floats (weighting of the original query, relevant artists,
                and irrelevant artists, respectively)}
    Returns: np.ndarray
    """
    q = input_doc_mat[query]
    dimension = len(q)
    rel_d, irrel_d = np.zeros(dimension), np.zeros(dimension)
    relevant, irrelevant = query_obj['relevant_artists'], query_obj['irrelevant_artists']
    len_rel, len_irrel = len(relevant), len(irrelevant)
    
    for r in range(len_rel): # Get centroid of relevant artists
        artist = relevant[r]
        rel_d = rel_d + input_doc_mat[artist_name_to_index[artist]]
        
    for i in range(len_irrel): # Get centroid of irrelevant artists
        artist = irrelevant[i]
        irrel_d = irrel_d + input_doc_mat[artist_name_to_index[artist]]
    
    rocchio = a * q
    if len_rel > 0:
        rocchio += b * rel_d / len_rel
    if len_irrel > 0:
        rocchio -= c * irrel_d / len_irrel
        
    return np.clip(rocchio, 0, None)

def cosine_similarity(query_vec, tfidf_mat=matrix):
    """ Returns numpy array of each artist's cosine similarity score with [query_vec]
    
    Params: {query_vec: np.ndarray - (k,)
             tfidf_mat: np.ndarray - d x k (where d is number of documents/artists,
                and rows are normalized)
    Returns: np.ndarray
    """
    scores = tfidf_mat.dot(query_vec)
    return scores

def get_filter_function(name, rel_artists, irrel_artists, avg_followers, percentage=0.2):
    """ Returns True if [name] has more followers than [percentage] * [avg_followers]
        and [name] is not part of user input ([rel_artists]).
    
    Parameters: {name: String
                 rel_artists: List
                 irrel_artists: List
                 avg_followers: Float
                 percentage: Float}
    Returns: Boolean
    """
    follower_threshold = avg_followers * percentage
    return name not in rel_artists and name not in irrel_artists and get_artist_follower_count(name) > follower_threshold

def minmax_scale(vec):
    """ Returns min/max scale of [vec].
    
    Parameters: {vec: np.ndarray}
    Returns: np.ndarray
    """
    min = np.min(vec)
    return (vec-min) / (np.max(vec) - min)

def get_rec_artists(query, ling_desc, disliked_artist, artist_name_to_index=artist_name_to_index):
    """ Returns list of recommended artists and their similarity scores 
        that are similar to [query] and dissimilar to [disliked_artist].
    
    Parameters: {query: String (liked artist)
                 ling_desc: String
                 disliked_artist: String
                 artist_name_to_index: Dict}
    Returns: List
    """
    if (query not in artist_name_to_index) or (disliked_artist and (disliked_artist not in artist_name_to_index)):
        return []
    idx = artist_name_to_index[query]
    
    query_obj = {
        'relevant_artists': [query] if query else [],
        'irrelevant_artists': [disliked_artist] if disliked_artist else []
    }
    query_vec = rocchio_update(idx, query_obj, c=0.8)
    
    cosine_scores = minmax_scale(cosine_similarity(query_vec))
    jaccard_scores = minmax_scale(rocchio_update(idx,query_obj,input_doc_mat=jaccard))
    ling_scores = ling_similarity(ling_desc)
    
    final_scores = cosine_scores + 2 * jaccard_scores + ling_scores
    final_scores /= 4 if ling_desc else 3
    
    sorted_indices = np.argsort(final_scores)
    rankings = [(artist_names[i], final_scores[i]) for i in sorted_indices[::-1]]
    
    average_followers = np.array([get_artist_follower_count(name) for name in query_obj['relevant_artists']]).mean()
    artist_ranking = list(filter(lambda x: get_filter_function(x[0], query_obj['relevant_artists'], query_obj['irrelevant_artists'], average_followers), rankings))
    return artist_ranking[:10]

def get_results(query, ling_desc, disliked_artist):
    """ Returns list of recommended artists who are similar to [query] and dissimilar
        to [disliked_artist] along with their similarity score, description and photo.
    
    Parameters: {query: String (liked artist)
                 ling_desc: String
                 disliked_artist: String}
    Returns: List
    """
    data = []
    top_rec_artists = get_rec_artists(query, ling_desc, disliked_artist)
    if (top_rec_artists == []):
        return []
    for artist, score in top_rec_artists:
        genres = ", ".join(set(get_artist_genres(artist)) & set(get_artist_genres(query)))
        data.append({
            'artist_name' : artist,
            'sim_score' : round(score * 100, 2),
            'artist_id' : get_artist_id(artist),
            'common_genres' : genres,
            'description' : get_artist_description(artist),
            'follower_count': get_artist_follower_count(artist),
            'img_url' : get_artist_photo(artist),
            'rating' : get_artist_rating(artist)
        })
    return data    

@irsystem.route('/', methods=['GET'])
def search():
    """ Returns UI rendering of results. """
    query = request.args.get('search')
    ling_desc = request.args.get('ling_desc')
    disliked_artist = request.args.get('disliked_artist')
    data = get_results(query, ling_desc, disliked_artist)
    all_artist_names = [s.replace('\'', '').replace('\"', '') for s in artist_names]

    if ((not query) and (not ling_desc) and (not disliked_artist)):       # empty query
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names)
    elif ((data == []) or (query == disliked_artist)):    # query returned no results, or liked artist and disliked artist are the same
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name": query, "ling_desc": ling_desc, "disliked_artist": disliked_artist})
    else:
        output_message = "Since you like " + query + "'s music, we recommend..."
        return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name": query, "ling_desc": ling_desc, "disliked_artist": disliked_artist})

from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd
import numpy as np
import zipfile
from app.irsystem.models.singernlp.ArtistReviewLoader import ArtistReviewLoader

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"

DATA_DIRECTORY = 'data/processed'
NUM_TFIDF_FILES = 5
TFIDF_FILE = DATA_DIRECTORY + '/tfidf_mat_compressed.csv'
ARTIST_DETAILS_PATH = DATA_DIRECTORY + '/compiled-w-songs_new.csv'

tf_idf = pd.read_csv(TFIDF_FILE)
artist_details = pd.read_csv(ARTIST_DETAILS_PATH)

artist_names = tf_idf.values[:,0]
artist_name_to_index = {artist_names[i]: i for i in range(len(artist_names))}
matrix = tf_idf.to_numpy()[:,1:]

test_arl = ArtistReviewLoader()

def find_artist(artist_name, csv):
    """ Returns index of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: Int
    """
    col = 1 if (csv.values[0, 0] == 0) else 0 # checking which column contains the list of artists
    try:
        return np.argwhere(csv.values[:, col] == artist_name)[0][0]
    except:
        return -1

def get_artist_description(artist_name):
    """ Returns description of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        followers = artist_details['followers'][find_artist(artist_name, artist_details)]
        return artist_name + " has " + str(followers) + " followers on Spotify."
    except:
        return "Couldn't find additional details on " + artist_name + ". "

def get_artist_photo(artist_name):
    """ Returns url of [artist_name]'s photo.
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        return artist_details['Image URL'][find_artist(artist_name, artist_details)]
    except:
        return "https://www.pngitem.com/pimgs/m/148-1487614_spotify-logo-small-spotify-logo-transparent-hd-png.png"

def rocchio_update(query, query_obj, input_doc_mat=matrix, \
        artist_name_to_index=artist_name_to_index,a=.3, b=.3, c=.8):
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

def cosine_similarity(query_vec, tfidf_mat=matrix, artist_names=artist_names):
    """ Returns ranking of artist names using cosine similarity with query_vec.
    
    Params: {query_vec: np.ndarray - (k,)
             tfidf_mat: np.ndarray - d x k (where d is number of documents/artists,
                and rows are normalized)
             artist_names: List}
    Returns: List
    """
    scores = tfidf_mat.dot(query_vec)
    ranking = np.argsort(scores)
    
    return [artist_names[i] for i in ranking[::-1]]

def get_rec_artists(query, ling_desc, disliked_artist, artist_name_to_index=artist_name_to_index):
    """ Returns list of recommended artists that are similar to [query] and dissimilar
        to [disliked_artist].
    
    Parameters: {query: String (liked artist)
                 ling_desc: String
                 disliked_artist: String
                 artist_name_to_index: Dict}
    Returns: List
    """
    if query not in artist_name_to_index:
        return []
    idx = artist_name_to_index[query]
    
    query_obj = {
        'relevant_artists': [query] if query else [],
        'irrelevant_artists': [disliked_artist] if disliked_artist else []
    }
    query_vec = rocchio_update(idx, query_obj)
    
    artist_ranking = list(filter(lambda x: x != query, cosine_similarity(query_vec)))
    return artist_ranking[:10]

def get_results(query, ling_desc, disliked_artist):
    """ Returns list of recommended artists who are similar to [query] and dissimilar
        to [disliked_artist] along with their name, description and photo.
    
    Parameters: {query: String (liked artist)
                 ling_desc: String
                 disliked_artist: String}
    Returns: List
    """
    data = []
    top_rec_artists = get_rec_artists(query, ling_desc, disliked_artist)
    if (top_rec_artists == []):
        return []
    for artist in top_rec_artists:
        data.append({'artist_name' : artist, 'description' : get_artist_description(artist), 'img_url' : get_artist_photo(artist)})
    return data    

@irsystem.route('/', methods=['GET'])
def search():
    """ Returns UI rendering of results. """
    query = request.args.get('search')
    ling_desc = request.args.get('ling_desc')
    disliked_artist = request.args.get('disliked_artist')
    data = get_results(query, ling_desc, disliked_artist)
    all_artist_names = [s.replace('\'', '').replace('\"', '') for s in artist_names]

    if (not query):       # empty query
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names)
    elif (data == []):    # query returned no results
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name": query, "ling_desc": ling_desc, "disliked_artist": disliked_artist})
    else:
        output_message = "Since you like " + query + "'s music, we recommend..."
        return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name": query, "ling_desc": ling_desc, "disliked_artist": disliked_artist})

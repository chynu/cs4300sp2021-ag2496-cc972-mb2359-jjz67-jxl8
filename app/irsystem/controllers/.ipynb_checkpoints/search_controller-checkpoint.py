from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sklearn.preprocessing import normalize
import pandas as pd
import numpy as np
import zipfile
import ssl

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"

ssl._create_default_https_context = ssl._create_unverified_context

tf_idf = pd.read_csv("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/data/processed/tfidf_mat_compressed.csv")
artist_details = pd.read_csv("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/removed_dups_new.csv")
jaccard = pd.read_csv("https://raw.githubusercontent.com/chynu/cs4300sp2021-ag2496-cc972-mb2359-jjz67-jxl8/master/data/processed/jaccard.csv",index_col=[0]).to_numpy()

artist_names = tf_idf.values[:,0]
artist_name_to_index = {artist_names[i]: i for i in range(len(artist_names))}
matrix = tf_idf.to_numpy()[:,1:]

def get_artist_song_id(artist_name):
    """ Returns song id of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        return artist_details['Song ID'][artist_name_to_index[artist_name]]
    except:
        return "no song"

def get_artist_url(artist_name):
    """ Returns url of [artist_name]'s profile.
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        return artist_details['Artist URL'][artist_name_to_index[artist_name]]
    except:
        return "no url"
    
def get_artist_description(artist_name):
    """ Returns description of [artist_name].
    
    Parameters: {artist_name: String}
    Returns: String
    """
    try:
        followers = artist_details['followers'][artist_name_to_index[artist_name]]
        return artist_name + " has " + str(followers) + " followers on Spotify."
    except:
        return "Couldn't find additional details on " + artist_name + ". "

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

def cosine_similarity(query_vec, tfidf_mat=matrix):
    """ Returns numpy array of each artist's cosine similarity score with [query_vec]
    
    Params: {query_vec: np.ndarray - (k,)
             tfidf_mat: np.ndarray - d x k (where d is number of documents/artists,
                and rows are normalized)
    Returns: np.ndarray
    """
    scores = tfidf_mat.dot(query_vec)
    return scores

def get_rec_artists(query, ling_desc, disliked_artist, artist_name_to_index=artist_name_to_index):
    """ Returns list of recommended artists and their similarity scores 
        that are similar to [query] and dissimilar to [disliked_artist].
    
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
    
    cosine_scores = cosine_similarity(query_vec)
    jaccard_scores = rocchio_update(idx,query_obj,input_doc_mat=jaccard)
    final_scores = (jaccard_scores[:,np.newaxis] + cosine_scores[:,np.newaxis]).flatten()
#    print(cosine_scores[:5], normalize(cosine_scores[:5, np.newaxis]), jaccard_scores[:5], normalize(jaccard_scores[:5, np.newaxis]), final_scores[:5])
    
    sorted_indices = np.argsort(final_scores)
    rankings = [(artist_names[i], final_scores[i]) for i in sorted_indices[::-1]]
    artist_ranking = list(filter(lambda x: x[0] not in query_obj['relevant_artists'], rankings))
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
        data.append({'artist_name' : artist, 'sim_score' : str(round(score, 2)), \
                    'description' : get_artist_description(artist), 'img_url' : get_artist_photo(artist)})
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
    elif(query and (query == disliked_artist)): #liked artist and disliked artist are the same
        output_message = ''
        return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name": query, "ling_desc": ling_desc, "disliked_artist": disliked_artist})
    else:
        output_message = "Since you like " + query + "'s music, we recommend..."
        return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=data,\
                               artist_names=all_artist_names,\
                               query_info={"artist_name": query, "ling_desc": ling_desc, "disliked_artist": disliked_artist})

from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"

# TODO: Remove the `sample_data` variable once we are able to dynamically retrieve data. This is here for demo purposes.
sample_data = [
	{'artist_name': 'Amerie', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/d/dc/Amerie_-_All_I_Have_album.jpg'},
	{'artist_name': 'Christina Aguilera', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/0/07/Christinaaguilera-christinaaguilera.jpg'},
	{'artist_name': 'Rhianna', 'description': 'Lorem ipsum', 'img_url': 'https://upload.wikimedia.org/wikipedia/en/3/32/Rihanna_-_Anti.png'}]

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
		return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
	else:
		output_message = "Based on your query, " + query + ", we recommend..."
		return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=sample_data)

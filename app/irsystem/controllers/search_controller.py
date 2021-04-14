from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Similar Singer"
net_id = "Alyssa Gao (ag2496), Celine Choo (cc972), Mahak Bindal (mb2359), Jerilyn Zheng (jjz67), Jasper Liang (jxl8)"
sample_data = [
	{'artist_name': 'Amerie', 'description': 'Lorem ipsum'},
	{'artist_name': 'Christina Aguilera', 'description': 'Lorem ipsum'},
	{'artist_name': 'Rhianna', 'description': 'Lorem ipsum'}]

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
		return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
	else:
		output_message = "Your search: " + query
		data = range(5)
		return render_template('search_results.html', name=project_name, netid=net_id, output_message=output_message, data=sample_data)


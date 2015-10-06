from flask import Flask, request, render_template, make_response, url_for, redirect
from werkzeug import secure_filename
from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient('mongodb://localhost:27017/')
db = client.test_database
fs = GridFS(db)

blocks = db.blocks

app = Flask(__name__)

#fs = GridFS(db)

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/file-upload', methods=['POST'])
def upload():
	print 'hi'
	file = request.files['file']
	print file
	print file.content_type
	filename = secure_filename(file.filename)
	print filename
	oid = fs.put(file, content_type=file.content_type, filename=filename)

	block = {}
	filez = []
	filez.append({
		'name': filename,
		'id': oid
	})
	block['files'] = filez
	block_id = blocks.insert_one(block).inserted_id

	return redirect(url_for('view_block', id=block_id))


@app.route('/<id>')
def view_block(id):
	block = blocks.find_one()
	return render_template('block.html', block=block, files=block['files'])

@app.route('/<id>/<filename>')
def view_file(id, filename):
	block = blocks.find_one({'_id': id})
	file = fs.get(block['files'][filename])
	response = make_response(file.read())
	response.mimetype = file.content_type
	return response

if __name__ == "__main__":
	app.run(debug=True)
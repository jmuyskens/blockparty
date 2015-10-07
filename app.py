from flask import Flask, request, render_template, make_response, url_for, redirect, jsonify
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


@app.route('/create', methods=['POST'])
def create():
	block = {}
	block['files'] = []
	block_id = blocks.insert_one(block).inserted_id
	print block_id
	return jsonify(**{'id': str(block_id)})


@app.route('/<id>/upload', methods=['POST'])
def upload(id):
	files = request.files.getlist('file')
	file_storage = []
	for file in files:
		filename = str(id) + '/' + secure_filename(file.filename)

		oid = fs.put(file, content_type=file.content_type, filename=filename)

		file_storage.append({
			'name': filename,
			'id': str(oid)
		})
	print file_storage
	print id
	print blocks.find_one({'_id':id})
	print blocks.find_one_and_update({'_id':id}, {'$set': {'files': file_storage}}, upsert=True)

	return jsonify(**{'num': len(file_storage)})


@app.route('/<id>')
def view_block(id):
	block = blocks.find_one({'_id':id})
	print block['files']
	return render_template('block.html', block=block, files=block['files'])


@app.route('/<id>/<filename>')
def view_file(id, filename):
	file = fs.find_one({'filename': id + '/' + filename})
	response = make_response(file.read())
	response.mimetype = file.content_type
	return response

if __name__ == "__main__":
	app.run(debug=True)

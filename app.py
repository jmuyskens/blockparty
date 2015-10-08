from collections import defaultdict
import markdown
import datetime
import os

from flask import Flask, request, render_template, make_response, url_for, redirect, jsonify
from bson.objectid import ObjectId
from werkzeug import secure_filename
from pymongo import MongoClient
from gridfs import GridFS
import jinja2_highlight
import jinja2

MONGODB_SETTINGS = {
    'db': os.getenv('MONGODB_DB', 'blockparty_dev'),
    'host': os.getenv('MONGODB_HOST', 'localhost'),
    'port': os.getenv('MONGODB_PORT', 27017),
    'username': os.getenv('MONGODB_USER', 'host'),
    'password': os.getenv('MONGODB_PASS', 'local') 
}

client = MongoClient(host=MONGODB_SETTINGS['host'], port=MONGODB_SETTINGS['port'])
db = client[MONGODB_SETTINGS['db']].authenticate(MONGODB_SETTINGS['username'], MONGODB_SETTINGS['password'], mechanism='SCRAM-SHA-1')
fs = GridFS(db)

blocks = db.blocks

# extend flask to use our jinja2 extensions
class MyFlask(Flask):
    jinja_options = dict(Flask.jinja_options)
    jinja_options.setdefault('extensions',
        []).append('jinja2_highlight.HighlightExtension')

app = MyFlask(__name__)

@app.template_filter('markdown')
def render_markdown(text):
	return jinja2.Markup(markdown.markdown(text))

@app.route('/', methods=['GET'])
def index():
	recent_blocks = list(blocks.find(sort=[('timestamp', -1)], limit=20))
	return render_template('index.html', blocks=recent_blocks)


@app.route('/create', methods=['POST'])
def create():
	block = {}
	block['files'] = []
	block['timestamp'] = datetime.datetime.utcnow()
	block['thumbnail'] = ''
	block_id = blocks.insert_one(block).inserted_id
	return jsonify(**{'id': str(block_id)})


@app.route('/<id>/upload', methods=['POST'])
def upload(id):
	files = request.files.getlist('file')
	block = blocks.find_one({'_id': ObjectId(id)})
	
	file_storage = []
	if block:
		file_storage = block['files']

	thumbnail = block['thumbnail']

	for file in files:
		filename = secure_filename(file.filename)

		if 'thumbnail' in filename:
			thumbnail = filename

		path = str(id) + '/' + filename
		oid = fs.put(file, content_type=file.content_type, filename=path)

		content_types = ['text/css', 'text/javascript', 'text/html', 'text/markdown']

		file.seek(0)

		content = ''
		if file.content_type in content_types:
			content = file.read()

		print content

		programming_languages = defaultdict(str)
		
		for lang in [('text/css', 'css'), ('text/html', 'html'), ('text/javascript', 'javascript')]:
			programming_languages[lang[0]] = lang[1]

		file_storage.append({
			'name': filename,
			'path': path,
			'type': file.content_type,
			'id': str(oid),
			'content': content,
			'programming_language': programming_languages[file.content_type]
		})

	blocks.find_one_and_update({'_id': ObjectId(id)}, {'$set': {'files': file_storage, 'thumbnail': thumbnail}}, upsert=True)

	return jsonify(**{'num': len(file_storage)})


@app.route('/<id>')
def view_block(id):
	block = blocks.find_one({'_id': ObjectId(id)})
	filenames = []

	if block:
		filenames = map(lambda x: x['name'], block['files'])

	index = {}
	readme = {}

	if 'index.html' in filenames:
		index = block['files'][filenames.index('index.html')]

	if not index:
		for i, filename in enumerate(filenames):
			if '.html' in filename:
				index = block['files'][i]
				break

	if 'README.md' in filenames:
		readme = block['files'][filenames.index('README.md')]

	return render_template('block.html', block=block, files=block['files'], index=index, readme=readme)


@app.route('/<id>/<filename>', methods=['GET', 'DELETE', 'POST'])
def view_file(id, filename):
	block = blocks.find_one({'_id': ObjectId(id)})
	path = id + '/' + filename
	filenames = map(lambda x: x['name'], block['files'])

	if request.method == 'GET':
		oid = block['files'][filenames.index(filename)]['id']
		file = fs.get(ObjectId(oid))
		response = make_response(file.read())
		response.mimetype = file.content_type
		return response

	elif request.method == 'DELETE':
		file = fs.find_one({'filename': id + '/' + filename})
		if file:
			fs.delete(file._id)
			block['files'].pop(filenames.index(filename))
			blocks.find_one_and_update({'_id': ObjectId(id)}, {'$set': {'files': block['files']}}, upsert=True)

	elif request.method == 'POST':
		print 'hi post'
		file = fs.find_one({'filename': id + '/' + filename})
		content = request.form['content']
		oid = fs.put(content, encoding='utf-8', content_type=file.content_type, filename=path)
		block['files'][filenames.index(filename)]['content'] = content
		block['files'][filenames.index(filename)]['id'] = str(oid)
		blocks.find_one_and_update({'_id': ObjectId(id)}, {'$set': {'files': block['files']}}, upsert=True)
		return redirect(url_for('view_block', id=id), 302)

if __name__ == "__main__":
	app.run(debug=True)

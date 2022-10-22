import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

# Function to get a database connection.
# This function connects to database with the name `database.db`
connection_nums = 0

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_nums = connection_nums + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get total amount of posts in the database
def get_total_posts():
    connection = get_db_connection()
    total_posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return len(total_posts)

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info("Main request successfull")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    app.logger.info(f"Getting data of post {post_id}")
    post = get_post(post_id)
    if post is None:
      app.logger.info(f"Post {post_id} not found!")
      return render_template('404.html'), 404
    else:
      app.logger.info(f"Got data of post {post_id}")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f"Show about page successfull")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    app.logger.info("Creating data....")
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.warn("Missing require field!")
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f"Created post data \n title: {title} \n content: {content} \n done.")
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health check endpoint
@app.route('/healthz') 
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK-health"}),
        status=200,
        mimetype='application/json'
    )
    return response

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    total_posts = get_total_posts()
    response = app.response_class(
        response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":{connection_nums},"post_count":total_posts}}),
          status=200,
          mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
   ## stream logs to app.log file
   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   stdout_handler = logging.StreamHandler(stream=sys.stdout)
   stderr_handler = logging.StreamHandler(stream=sys.stderr)
   handlers = [stderr_handler, stdout_handler]
 
   format_output = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

   logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)
   app.run(host='0.0.0.0', port='3111')

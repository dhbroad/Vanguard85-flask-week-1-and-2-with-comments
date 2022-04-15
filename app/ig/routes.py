from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.apiauthhelper import token_required


ig = Blueprint('ig', __name__, template_folder='ig_templates')

from .forms import CreatePostForm, UpdatePostForm
from app.models import db, Post, User


@ig.route('/posts')
def posts():
    posts = Post.query.all()[::-1] # query comes from SQAlchemy. This specific query gets all of the existing posts from our Post model database and sorts them in reverse order [::-1] because we want the newest on top
    return render_template('posts.html', posts = posts)

@ig.route('/create-post', methods=["GET", "POST"])
@login_required # login_required is a built-in
def createPost():
    form = CreatePostForm()
    if request.method == "POST":
        if form.validate():
            title = form.title.data
            img_url = form.img_url.data
            caption = form.caption.data

            # Creating a Post instance. The parameters need to match up with how you created the model
            post = Post(title, img_url, caption, current_user.id) # current_user is a global variable we have access to because of LoginManager in our __init__.py, but we still have to import current user 

            db.session.add(post)
            db.session.commit()   

            return redirect(url_for('home'))         

    return render_template('createpost.html', form = form)

@ig.route('/posts/<int:post_id>') # <> creates a variable. The type of variable has to be specified, so we specified it as int:
def individualPost(post_id): # because we are getting a variable, we need to accept it in our function
    post = Post.query.filter_by(id=post_id).first() # filter_by comes from a Flask query command. post_id is what's being passed in, and id is the name of the column
    if post is None:
        return redirect(url_for('ig.posts'))
    return render_template('individual_post.html', post = post)

@ig.route('/posts/update/<int:post_id>', methods=["GET","POST"]) # you GET the website and you UPDATE (POST) the information
@login_required
def updatePost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return redirect(url_for('ig.posts'))
    if post.user_id != current_user.id:
        return redirect(url_for('ig.posts'))
    form = UpdatePostForm()
    if request.method == "POST":
        if form.validate():
            title = form.title.data
            img_url = form.img_url.data
            caption = form.caption.data

            # update the original post (as opposed to creating a new one like in createPost)
            post.title = title
            post.image = img_url
            post.caption = caption

            # Also no longer need to 'add' to database, like in createPost. Instead you just commit it

            db.session.commit()   

            return redirect(url_for('home'))         
    return render_template('updatepost.html', form=form, post = post)


@ig.route('/posts/delete/<int:post_id>', methods=["POST"]) # not a GET request because you are really just POSTing to delete
@login_required
def deletePost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return redirect(url_for('ig.posts'))
    if post.user_id != current_user.id:
        return redirect(url_for('ig.posts'))

    db.session.delete(post)
    db.session.commit()
               
    return redirect(url_for('ig.posts'))


# 
# 
#   API STARTS HERE
# 
#

@ig.route('/api/posts')
def apiPosts():
    posts = Post.query.all()[::-1]
    return {
        'status': 'ok',
        'total_results': len(posts),
        'posts': [p.to_dict() for p in posts]
        }

@ig.route('/api/posts/<int:post_id>')
def apiSinglePost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return {
            'status': 'not ok',
            'total_results': 0,
        }
    return {
        'status': 'ok',
        'total_results': 1,
        'post': post.to_dict()
        }


@ig.route('/api/create-post', methods=["POST"])
@token_required
def apiCreatePost(user):
    data = request.json

    title = data['title']
    img_url = data['img_url']
    caption = data['caption']

    post = Post(title, img_url, caption, user.id)

    db.session.add(post)
    db.session.commit()   

    return {
        'status': 'ok',
        'message': 'Successfully create a new post.',
        'post': post.to_dict()
    }

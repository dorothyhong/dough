"""Deal with post req."""
import pathlib
import uuid
import os
import flask
from flask import request, session, redirect, url_for
import insta485
from insta485.views.index import get_like_status


# needs to return something
@insta485.app.route('/likes/', methods=['POST'])
def handle_like():
    """Post likes."""
    if "username" in session:
        username = session["username"]
        # Extracting data from POST request
        operation = request.form.get('operation')
        post_id = request.form.get('postid')
        target_url = flask.request.args.get('target', '/')

        if operation == 'like':
            if get_like_status(post_id, username):
                flask.abort(409)
            add_like(post_id, username)
        elif operation == 'unlike':
            if not get_like_status(post_id, username):
                flask.abort(409)
            remove_like(post_id, username)
        else:
            flask.abort(400)
        return flask.redirect(flask.url_for("show_post",
                              postid_url_slug=post_id))
    return redirect(target_url)


# get_like_status

# def is_already_liked(post_id, user):
#     """Post already liked."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         SELECT likeid
#         FROM likes
#         WHERE postid = ? AND owner = ?
#     """, (post_id, user,))
#     row = cursor.fetchone()
#     if row is None:
#         return False
#     return True


def add_like(post_id, user):
    """Post add like."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO likes (owner, postid, created)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (user, post_id))


def remove_like(post_id, user):
    """Post  remove like."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM likes
        WHERE owner = ? AND postid = ?
    """, (user, post_id))


@insta485.app.route('/comments/', methods=['POST'])
def handle_comment():
    """Post /commnets/."""
    if "username" in session:
        username = session["username"]
        operation = request.form.get('operation')
        post_id = request.form.get('postid')
        comment_id = request.form.get('commentid')
        text = request.form.get('text')
        target_url = request.args.get('target', '/')
        # Check if the target URL is not set, redirect to '/'
        if not target_url:
            return redirect(url_for('show_index'))
        if operation == 'create' and not text:
            flask.abort(400)
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        print(operation)
        print(comment_id)
        if operation == 'create':
            cursor.execute("""
                INSERT INTO comments (commentid, owner, postid, text, created)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (comment_id, username, post_id, text))
        elif operation == 'delete':
            cursor.execute("""
                DELETE FROM comments
                WHERE commentid = ?
            """, (comment_id,))
        else:
            flask.abort(400)
        connection.commit()
        return redirect(target_url)
    return redirect(url_for('show_login'))


@insta485.app.route('/posts/', methods=['POST'])
def handle_post():
    """Post /posts/."""
    if "username" in session:
        username = session["username"]
        operation = request.form.get('operation')
        post_id = request.form.get('postid')
        target_url = request.args.get('target', f'/users/{username}/')
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        if operation == "create":
            # Unpack flask object
            fileobj = flask.request.files["file"]
            filename = fileobj.filename
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"

            # Save to disk
            path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
            fileobj.save(path)

            cursor.execute('''
                INSERT INTO posts (postid, filename, owner, created)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (post_id, uuid_basename, username))

        print(operation)
        if operation == "delete":
            cursor.execute("""
                SELECT filename
                FROM posts
                WHERE postid = ? and owner = ?
            """, (post_id, username))
            result = cursor.fetchone()
            if not result:
                flask.abort(403)
            os.remove(os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                result['filename']))
            cursor.execute("""
                DELETE FROM posts
                WHERE postid = ?
            """, (post_id,))

        # connection.commit()
        return redirect(target_url)
    return redirect(url_for('show_login'))


@insta485.app.route('/following/', methods=['POST'])
def handle_follow():
    """Post /following/."""
    if "username" in session:
        username1 = session["username"]
        operation = request.form.get('operation')
        username2 = request.form.get('username')
        target_url = request.args.get('target', '/')
        # Check if the target URL is not set, redirect to '/'
        if not target_url:
            return redirect(url_for('show_index'))
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        if operation == 'follow':
            if is_already_following(username1, username2):
                flask.abort(409)
            cursor.execute("""
                INSERT INTO following (username1, username2, created)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (username1, username2))
        elif operation == 'unfollow':
            if not is_already_following(username1, username2):
                flask.abort(409)
            cursor.execute("""
                DELETE FROM following
                WHERE username1 = ? AND username2 = ?
            """, (username1, username2))
        else:
            # Handle invalid operation
            # (you may want to redirect to an error page)
            flask.abort(400)

        connection.commit()

        return redirect(target_url)
    return redirect(url_for('show_login'))


def is_already_following(username1, username2):
    """Is already following."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM following
        WHERE username1 = ? AND username2 = ?
    """, (username1, username2))
    already_following = cursor.fetchone()
    if already_following is None:
        return False
    return True

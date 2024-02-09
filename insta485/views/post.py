"""Deal with Posts."""
import flask
from flask import session
import arrow
import insta485
from insta485.views.index import get_like_status, get_likes_count
from insta485.views.index import get_comments_for_post
from insta485.views.index import get_user_profile_picture
# from insta485.views.accounts import get_post_check


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    """Display /posts/<postid_url_slug>/ route."""
    if "username" in session:
        logged_in_user = session["username"]
        post = get_post_by_id(postid_url_slug)
        print(post)
        comments = get_comments_for_post(postid_url_slug)
        is_liked = get_like_status(postid_url_slug, logged_in_user)

        context = {
            "logname": logged_in_user,
            "post": {
                "postid": post["postid"],
                "timestamp": arrow.get(post["created"]).humanize(),
                "owner": post["owner"],
                "likes": get_likes_count(post["postid"]),
                "is_liked": is_liked,
                "comments": comments,
                "img_url": '/uploads/' + post["filename"],
                "owner_img_url": '/uploads/' +
                get_user_profile_picture(post["owner"]),
            }
        }

        return flask.render_template("post.html", **context)
    return flask.redirect(flask.url_for('show_login'))


def get_post_check(connection, postid):
    """Get post by id."""
    cursor = connection.cursor()
    cursor.execute("""
        SELECT postid, filename, owner, created
        FROM posts
        WHERE postid = ?;
    """, (postid,))
    post = cursor.fetchone()
    return post


def get_post_by_id(postid):
    """Get post by id."""
    connection = insta485.model.get_db()
    post = get_post_check(connection, postid)
    insta485.model.close_db("error")
    return post

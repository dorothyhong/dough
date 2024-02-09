"""Deal with Users."""
import flask
from flask import session
import insta485
from insta485.views.accounts import get_recent_posts, get_fullname


@insta485.app.route('/users/<username>/')
def show_user(username):
    """Display / route."""
    if "username" in session:
        logged_in_user = session["username"]
        posts = get_recent_posts(username)
        num_posts = len(posts)
        followers = get_followers(username)
        # num_posts = get_num_posts(username)
        num_followers = len(followers)
        num_following = len(get_following(username))
        logged_user_is_username = logged_in_user == username
        fullname = get_fullname(username)
        logged_in_user_follow_username = False
        for follower in followers:
            if follower['username1'] == logged_in_user:
                logged_in_user_follow_username = True
                break  # exit the loop once a match is found

        context = {
            "logname": logged_in_user,
            "username": username,
            "fullname": fullname,
            "logname_follows_username": logged_in_user_follow_username,
            "logged_user_is_username": logged_user_is_username,
            "followers": num_followers,
            "following": num_following,
            "total_posts": num_posts,
            "posts": [],
        }

        for post in posts:
            post_data = {
                "postid": post["postid"],
                "img_url": '/uploads/' + post["filename"],
            }
            context["posts"].append(post_data)

        # still need to deal with forms
        return flask.render_template("user.html", **context)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/users/<username>/followers/')
def show_user_followers(username):
    """Followers / route."""
    if "username" in session:
        logged_in_user = session["username"]
        followers = get_followers(username)
        logged_user_is_username = logged_in_user == username
        # user_img_url = get_user_profile_picture(username)
        logged_in_user_follow_username = False

        for follower in followers:
            if follower['username1'] == logged_in_user:
                logged_in_user_follow_username = True

        context = {
            "logname": logged_in_user,
            "username": username,
            "logname_follows_username": logged_in_user_follow_username,
            "logged_user_is_username": logged_user_is_username,
            "followers": []
        }

        logname_following = get_following(logged_in_user)
        for follower in followers:
            # is logged-in-user following
            # each person in the followers list
            following_bul = False
            for follow in logname_following:
                if follower["username1"] == follow["username2"]:
                    following_bul = True

            # since the templates use follower.img,
            # we needed to track a lot of the information
            # under the follower data object
            follower_data = {
                "username": follower["username1"],
                "user_img_url": '/uploads/'
                + get_user_profile_picture(follower["username1"]),
                "logname_follows_username": following_bul
            }
            context["followers"].append(follower_data)

        return flask.render_template("followers.html", **context)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/users/<username>/following/')
def show_user_following(username):
    """Following / route."""
    if "username" in session:
        logged_in_user = session["username"]
        following = get_following(username)
        logged_user_is_username = logged_in_user == username
        # user_img_url = get_user_profile_picture(username)
        logged_in_user_follow_username = False

        for f in following:
            if f['username2'] == logged_in_user:
                logged_in_user_follow_username = True

        context = {
            "logname": logged_in_user,
            "username": username,
            "logname_follows_username": logged_in_user_follow_username,
            "logged_user_is_username": logged_user_is_username,
            "following": []
        }

        logged_in_user_following = get_following(logged_in_user)

        for f in following:
            following_bul = False
            for follow in logged_in_user_following:
                if f["username2"] == follow["username2"]:
                    following_bul = True
                    break

            following_data = {
                "username": f["username2"],
                "user_img_url": '/uploads/'
                + get_user_profile_picture(f["username2"]),
                "logname_follows_username": following_bul
            }
            context["following"].append(following_data)

        return flask.render_template("following.html", **context)
    return flask.redirect(flask.url_for('show_login'))


# def get_recent_posts(user):
#     """Get recent posts."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         SELECT postid, filename, owner, created
#         FROM posts
#         WHERE owner = ?
#         ORDER BY postid DESC;
#     """, (user,))
#     posts = cursor.fetchall()
#     connection = insta485.model.close_db("error")

#     return posts


def get_followers(user):
    """Get followers."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT username1
        FROM following
        WHERE username2 = ?
        ORDER BY created DESC
    """, (user,))
    followers = cursor.fetchall()
    connection = insta485.model.close_db("error")

    return followers


def get_following(user):
    """Get following."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT username2
        FROM following
        WHERE username1 = ?
        ORDER BY created DESC
    """, (user,))
    following = cursor.fetchall()
    connection = insta485.model.close_db("error")
    return following


# def get_fullname(user):
#     """Get Full name."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         SELECT fullname
#         FROM users
#         WHERE username = ?
#     """, (user,))
#     name = cursor.fetchone()
#     # connection = insta485.model.close_db("error")
#     return name['fullname']


def get_user_profile_picture(username):
    """Get profile picture."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT filename
        FROM users
        WHERE username = ?
    """, (username,))
    profile_picture = cursor.fetchone()
    # connection = insta485.model.close_db("error")

    return profile_picture['filename']

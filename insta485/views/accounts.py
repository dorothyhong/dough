"""Deal with accounts."""
import os
import uuid
import pathlib
import hashlib
import flask
from flask import request, redirect, url_for, abort, session
import insta485
from insta485.views.index import get_user_profile_picture, get_posts


@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Display /accounts/login/ route."""
    if flask.session.get('username'):
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/create/', methods=['GET'])
def show_create():
    """Display /accounts/create/ route."""
    return flask.render_template("create.html")


@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Display /accounts/delete/ route."""
    if "username" in session:
        logged_in_user = session["username"]
        context = {"logname": logged_in_user}
        return flask.render_template("delete.html", **context)
    return flask.redirect(url_for('show_login'))


@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display /accounts/edit/ route."""
    if "username" in session:
        logged_in_user = session["username"]
        context = {"logname": logged_in_user,
                   "fullname": get_fullname(logged_in_user),
                   "user_img_url": '/uploads/' +
                   get_user_profile_picture(logged_in_user),
                   "email": get_user_email(logged_in_user)
                   }
        return flask.render_template("edit.html", **context)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/accounts/password/', methods=['GET'])
def show_password():
    """Display /accounts/password/ route."""
    if "username" in session:
        logged_in_user = session["username"]
        context = {"logname": logged_in_user}
        return flask.render_template("password.html", **context)
    return flask.redirect(flask.url_for('show_login'))

    # If GET request, render the create account form


@insta485.app.route('/accounts/auth/', methods=['GET'])
def show_auth():
    """Display /accounts/auth/ route."""
    if "username" in session:
        return '', 200
    abort(403)


def get_user_email(username):
    """Get user email."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM users WHERE username = ?;", (username,))
    profile_picture = cursor.fetchone()
    connection = insta485.model.close_db("error")
    return profile_picture['email']


def is_valid_login(username, password):
    """Check if the login credentials are valid."""
    # For illustration purposes, a simple check is implemented here.
    return username == "example" and password == "password"


# def get_user_profile_picture(username):
#     """Get user profile picture."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()
#     cursor.execute("SELECT filename FROM users WHERE username = ?;",
#                    (username,))
#     profile_picture = cursor.fetchone()
#     connection = insta485.model.close_db("error")
#     return profile_picture['filename']


def get_fullname(user):
    """Get fullname."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT fullname
        FROM users
        WHERE username = ?
    """, (user,))

    name = cursor.fetchone()
    connection = insta485.model.close_db("error")
    return name['fullname']


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout user."""
    flask.session.clear()
    return flask.redirect(flask.url_for('show_login'))


# def authenticate(username, password):
#     """Authenticate user."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()

#     # Fetch the user from the database
#     cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?",
#                    (username,))
#     result = cursor.fetchone()['COUNT(*)']
#     check = result > 0

#     if check:
#         stored_passwd = get_old_passwd(username)
#         return verify_password(password, stored_passwd['password'])

#     return False

def authenticate(username, password):
    """Authenticate user."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()

    # Fetch the user from the database
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()['COUNT(*)']
    user_exists = result > 0

    if user_exists:
        print("HELLOOOOO")
        stored_passwd = get_old_passwd(username)
        if stored_passwd:
            return verify_password(password, stored_passwd['password'])

    return False



@insta485.app.route('/accounts/', methods=['POST'])
def handle_accounts_operations():
    """Post /accounts/."""
    operation = request.form['operation']
    target = request.args.get('target', '/')

    if operation == 'login':
        login_op(target)

    elif operation == 'create':
        create_op(target)

    if 'username' not in session:
        abort(403)

    if operation == 'edit_account':
        return redirect(edit_account_op(target))

    if operation == 'delete':
        return redirect(delete_op(target))

    if operation == 'update_password':
        return redirect(update_password_op(target))

    return flask.redirect(flask.url_for('show_index'))


def edit_account_op(target):
    """Edit account operation."""
    username = session["username"]
    fileobj = request.files['file']
    filename = fileobj.filename
    fullname = request.form.get('fullname')
    email = request.form.get('email')

    if fullname == "" or email == "":
        abort(400)

    connection = insta485.model.get_db()
    cursor = connection.cursor()

    if filename == "":
        cursor.execute("""
            UPDATE users
            SET fullname = ?, email = ?
            WHERE username = ?
        """, (fullname, email, username))
    else:
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = os.path.join(insta485.app.config["UPLOAD_FOLDER"],
                            uuid_basename)
        fileobj.save(path)
        cursor.execute("""
            UPDATE users
            SET fullname = ?, email = ?, filename = ?
            WHERE username = ?
        """, (fullname, email, uuid_basename, username))

    return target


def delete_op(target):
    """Delete operation."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()

    if 'username' not in session:
        abort(403)

    username = session["username"]
    user_posts = get_recent_posts(username)
    cursor.execute("SELECT filename FROM users WHERE username = ?",
                   (username,))
    icon = cursor.fetchone()['filename']

    path = os.path.join(insta485.app.config['UPLOAD_FOLDER'], icon)
    if os.path.exists(path):
        os.remove(path)

    # Delete user's posts and related entries
    for post in user_posts:
        name = post['filename']
        p_p = os.path.join(insta485.app.config['UPLOAD_FOLDER'], name)
        if os.path.exists(p_p):
            os.remove(p_p)

    # Delete user entries
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))

    # Commit the changes to the database
    connection.commit()

    # Clear the user's session
    session.clear()

    # Redirect to a URL
    return target


def update_password_op(target):
    """Update password operation."""
    if 'username' not in session:
        abort(403)

    username = session["username"]
    password = request.form.get('password')
    new_password1 = request.form.get('new_password1')
    new_password2 = request.form.get('new_password2')
    target = request.args.get('target', '/')

    if password == "" or new_password1 == "" or new_password2 == "":
        abort(400)

    og_psswd = get_old_passwd(username)

    if not verify_password(password, og_psswd['password']):
        abort(403)

    password_db_string_1 = gen_hashed_passwd(new_password1)
    password_db_string_2 = gen_hashed_passwd(new_password2)

    if not verify_password(new_password1, password_db_string_2):
        abort(401)

    change_password(username, password_db_string_1)
    return target


def login_op(target):
    """Login operation."""
    username = request.form['username']
    password = request.form['password']
    if not username or not password:
        abort(400)

    if authenticate(username, password):
        session['username'] = username
    return redirect(target)


def generate_uuid_basename(filename):
    """Generate uuid."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    return f"{stem}{suffix}"


def save_file_to_disk(file, uuid_basename):
    """Save file to disk."""
    path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    file.save(path)
    return path


def compute_password_hash(password):
    """Compute password hash."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])


def check_username_availability(username):
    """Check username availability."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None


def create_user_in_database(username, fullname,
                            email, filename, password_db_string):
    """Create user in database."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (username, fullname, email,"
        + "filename, password, created) " +
        "VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (username, fullname, email, filename, password_db_string)
    )
    connection.commit()


def create_op(target):
    """Create op."""
    username = request.form.get('username')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    file = request.files['file']
    filename = file.filename

    uuid_basename = generate_uuid_basename(filename)
    path = save_file_to_disk(file, uuid_basename)

    if not all([username, password, fullname, email, path]):
        abort(400)

    password_db_string = compute_password_hash(password)

    if check_username_availability(username):
        abort(409)  # Conflict

    create_user_in_database(username,
                            fullname, email, uuid_basename, password_db_string)

    session['username'] = username
    return redirect(target)


def gen_hashed_passwd(password, salt=None):
    """Get hashed password."""
    algorithm = 'sha512'
    if not salt:
        # if no salt is provided, generate a new one
        salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])


def get_old_passwd(username):
    """Get old password."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT password
        FROM users
        WHERE username = ?
    """, (username,))
    og_password = cursor.fetchone()
    return og_password


def change_password(username, hashed_password):
    """Change password."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE users SET password = :hashed_password WHERE username = :username
        """, {'hashed_password': hashed_password, 'username': username})


def verify_password(password, original_password_hash):
    """Verify password."""
    split = original_password_hash.split('$')

    salt = split[1] if len(split) == 3 else None
    password_hash = gen_hashed_passwd(password, salt)
    return password_hash == original_password_hash


def get_post_by_id(postid):
    """Get post by id."""
    query = """
        SELECT postid, filename, owner, created
        FROM posts
        WHERE postid = ?;
    """
    return get_posts(query, (postid,))


def get_recent_posts(user):
    """Get recent posts."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT postid, filename, owner, created
        FROM posts
        WHERE owner = ?
        ORDER BY postid DESC;
    """, (user,))
    posts = cursor.fetchall()
    # connection = insta485.model.close_db("error")

    return posts

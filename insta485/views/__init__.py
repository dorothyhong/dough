"""Views, one for each Insta485 page."""
# index
from insta485.views.index import show_index
from insta485.views.index import serve_file

# accounts
from insta485.views.accounts import show_login
from insta485.views.accounts import show_create
from insta485.views.accounts import show_delete
from insta485.views.accounts import show_password
from insta485.views.accounts import show_edit
from insta485.views.accounts import show_auth
from insta485.views.accounts import logout
from insta485.views.accounts import handle_accounts_operations

# explore
from insta485.views.index import show_explore

# post
from insta485.views.post import show_post

# user
from insta485.views.user import show_user
from insta485.views.user import show_user_followers
from insta485.views.user import show_user_following

# post_req
from insta485.views.post_req import handle_like
from insta485.views.post_req import handle_comment
from insta485.views.post_req import handle_post
from insta485.views.post_req import handle_follow

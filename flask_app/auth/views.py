from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from common.db_api import get_admin_user
from common.models.user import UserAdmin
from flask_app.forms import LoginForm

auth_app = Blueprint("auth_app", __name__)


@auth_app.route('/admin/login/', methods=['GET', 'POST'], endpoint="login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.index"))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = get_admin_user(form.username.data)
        if user is None:
            return render_template("auth/login.html", form=form, error="username doesn't exist")
        if not user.check_password(form.password.data):
            return render_template("auth/login.html", form=form, error="invalid username or password")

        login_user(user)
        return redirect(url_for("admin.index"))

    return render_template("auth/login.html", form=form)

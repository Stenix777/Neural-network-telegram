import copy
import json

import flask_login as login
from flask import redirect, request, url_for
from flask_admin import AdminIndexView, expose
from flask_app.forms import EditForm
from flask_login import current_user


def get_json_data():
    with open('common/settings.json', 'r') as json_file:
        data = json.load(json_file)

    return data


def update_json(data):
    old_data = get_json_data()
    result = copy.deepcopy(old_data)
    for c, settings in old_data.items():
        for key, info in settings.items():
            if new_value := data.get(key):
                result[c][key]['value'] = new_value

    with open('common/settings.json', 'w') as json_file:
        json.dump(result, json_file, indent=4, ensure_ascii=False)


class MyAdminIndexView(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('auth_app.login'))
        form = EditForm()

        if request.method == 'POST' and form.validate_on_submit():
            update_json(request.form)

        data = get_json_data()

        return self.render('admin/index.html', title='Admin Panel', data=data, form=form)

    @expose('/logout/')
    def logout_page(self):
        login.logout_user()
        return redirect(url_for('admin.index'))

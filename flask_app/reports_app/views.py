from flask import Blueprint, render_template

from common.db_api import sync_get_links, sync_get_object_by_id
from common.models import User

reports_app = Blueprint(name="reports", import_name=__name__, url_prefix="/reports")


@reports_app.get("/links/<int:user_id>/")
def links_list_view(user_id: int):
    user = sync_get_object_by_id(User, user_id)
    if not user or not user.is_admin:
        return render_template("reports_app/503.html")

    return render_template("reports_app/links.html", links=sync_get_links(user_id))




from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BooleanEqualFilter

from common.models import (ImageQuery, Invoice, ReferalLink, Report, Tariff,
                           TextGenerationRole, TextQuery, User, VideoQuery)
from flask_app.extensions import admin, db


class AdminView(ModelView):
    pass


class TariffView(AdminView):
    form_excluded_columns = ("invoices", "users")


class UserAdminView(AdminView):
    column_display_pk = True
    can_create = True
    form_columns = ['id', 'username', 'first_name', 'last_name', 'is_active', 'is_admin', 'gemini_daily_limit',
                    'kandinsky_daily_limit', 'sd_daily_limit', 'token_balance', 'txt_model', 'txt_model_role_id',
                    'img_model', 'tts_mode', 'text_session_id', 'update_daily_limits_time', 'tariff', 'payment_time',
                    'payment_tries', 'recurring', 'first_payment']
    
    column_searchable_list = ('id', 'username')

    # column_filters = [BooleanEqualFilter(column=User.is_active, name='Active1')]
    # column_filters = ('is_active',)


class ReferalLinkView(AdminView):
    pass


class InvoiceView(AdminView):
    column_display_pk = True
    form_excluded_columns = ("invoices", "users")


class TextGenerationRoleView(AdminView):
    pass


class ReportView(AdminView):
    column_list = ("date", )
    form_excluded_columns = ("id", )


admin.add_view(UserAdminView(User, db.session, name='Пользователи'))
admin.add_view(TariffView(Tariff, db.session, name='Тарифы'))
admin.add_view(InvoiceView(Invoice, db.session, name='Счета'))
admin.add_view(TextGenerationRoleView(TextGenerationRole, db.session, name='Роли'))
admin.add_view(ReportView(Report, db.session, name='Отчёты'))

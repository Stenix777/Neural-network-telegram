from flask import Blueprint, Response, redirect, render_template, request
from loguru import logger

from common.db_api import (sync_create_obj, sync_get_object_by_id,
                           sync_update_object, update_subscription)
from common.models import Invoice, Tariff, User
from common.services import robokassa

payments_app = Blueprint(name="payments", import_name=__name__, url_prefix="/payments")


@payments_app.get("/redirect/<tariff_id>/<user_id>/")
def redirect_view(tariff_id: int, user_id: int):
    tariff: Tariff = sync_get_object_by_id(Tariff, tariff_id)
    user: User = sync_get_object_by_id(User, user_id)

    if not user.first_payment and tariff.is_trial:
        tariff: Tariff = sync_get_object_by_id(Tariff, tariff.main_tariff_id)

    if tariff.is_extra and user.tariff and not user.tariff.is_trial:
        price = int(tariff.price / 2)
    else:
        price = tariff.price

    invoice: Invoice = sync_create_obj(Invoice, user_id=user_id, tariff_id=tariff_id, sum=price)

    redirect_url = robokassa.gen_pay_url(user_id=user_id, inv_id=invoice.id, price=price,
                                         tariff_desc=tariff.description, recurring=not tariff.is_extra)

    return redirect(redirect_url)


@payments_app.get("/result/")
def result_view():
    try:
        inv_id = request.args.get("InvId")
        price = request.args.get("OutSum")
        signature = request.args.get("SignatureValue")

        invoice: Invoice = sync_get_object_by_id(Invoice, int(inv_id))

        if invoice.is_paid:
            return Response(f"OK{inv_id}", status=200)

        if not robokassa.check_signature(inv_id=inv_id, price=price, recv_signature=signature):
            logger.error(f"Check signature ERROR | {inv_id}")
            return Response("Check signature ERROR", status=403)

        user: User = sync_get_object_by_id(User, id_=invoice.user_id, relations=[User.referral_links])
        tariff: Tariff = sync_get_object_by_id(Tariff, id_=invoice.tariff_id)

        if tariff.is_extra:
            sync_update_object(user, token_balance=user.token_balance + tariff.token_balance)
        else:
            update_subscription(user=user, invoice=invoice, tariff=tariff)

        if user.referral_links:
            link = user.referral_links[0]
            sync_update_object(link, buys_cnt=link.buys_cnt + 1, buys_sum=link.buys_sum + int(float(price)))

        sync_update_object(invoice, sum=int(float(price)), is_paid=True)

        logger.info(f"Success payment <{user.id}> | <{price}>")

        return Response(f"OK{inv_id}", status=200)

    except Exception as error:
        logger.error(f'View subscription ERROR | InvID {inv_id if inv_id else "None"} | {error}')  # noqa
        return Response("Renewal subscription ERROR", status=500)


@payments_app.get("/success/")
def success_view():
    return render_template("user_templates/payment_success.html")

import json
from hashlib import md5
from urllib.parse import urlencode

import requests
from aiohttp import ClientSession
from loguru import logger


class Robokassa:
    def __init__(self, login, password_1, password_2):
        self.login = login
        self.password_1 = password_1
        self.password_2 = password_2
        self.payment_url = "https://auth.robokassa.ru/Merchant/Index.aspx"
        self.recurring_url = "https://auth.robokassa.ru/Merchant/Recurring"

    @staticmethod
    def calc_signature(*args) -> str:
        return md5(":".join(str(arg) for arg in args).encode()).hexdigest()

    def check_signature(self, inv_id: int, price: int, recv_signature: str) -> bool:
        signature = self.calc_signature(price, inv_id, self.password_2)
        return recv_signature.lower() == signature.lower()

    @staticmethod
    def gen_receipt(price: int, tariff_desc: str) -> str:
        return json.dumps(
            {
                "sno": "usn_income",
                "items": [{"name": tariff_desc, "quantity": 1, "sum": price, "tax": "none"}],
            }
        )

    def gen_payment_data(
        self, user_id: int | str, inv_id: int, price: int, tariff_desc, recurring: bool, mother_inv_id: int = None
    ) -> dict:
        receipt = self.gen_receipt(price=price, tariff_desc=tariff_desc)

        data = {
            "MerchantLogin": self.login,
            "OutSum": price,
            "invoiceID": inv_id,
            "Description": f"{tariff_desc} | {user_id}",
            "SignatureValue": self.calc_signature(self.login, price, inv_id, receipt, self.password_1),
            "Recurring": recurring,
            "Receipt": receipt,
        }

        if mother_inv_id:
            data["PreviousInvoiceID"] = mother_inv_id
            data["Description"] = "Продление " + data["Description"]
            del data["Recurring"]

        return data

    def gen_pay_url(self, user_id: int, inv_id: int, price: int, tariff_desc: str, recurring: bool) -> str:
        data = self.gen_payment_data(user_id=user_id, inv_id=inv_id, price=price, tariff_desc=tariff_desc,
                                     recurring=recurring)

        return f"{self.payment_url}?{urlencode(data)}"

    def recurring_request(self, user_id: int | str, inv_id: int, price: int, tariff_desc,
                          mother_inv_id: int = None) -> None:
        data = self.gen_payment_data(user_id=user_id, inv_id=inv_id, price=price, tariff_desc=tariff_desc,
                                     mother_inv_id=mother_inv_id, recurring=True)

        response = requests.post(url=self.recurring_url, data=data)

        if response.ok:
            logger.info(f"Recurring payment send | {user_id}")
        else:
            logger.error(f"Recurring payment error | {user_id} | {response.text}")

    async def async_recurring_request(self, user_id: int, inv_id: int, price: int, desc: str, mother_inv_id: int
                                      ) -> None:
        data = self.gen_payment_data(user_id=user_id, inv_id=inv_id, price=price, tariff_desc=desc,
                                     mother_inv_id=mother_inv_id, recurring=True)

        async with ClientSession() as session:
            async with session.post(url=self.recurring_url, data=data) as response:
                if response.ok:
                    logger.info(f"Recurring request SUCCESS | <{user_id}>")
                else:
                    logger.error(f"Recurring request ERROR | <{user_id}> | {await response.text()}")

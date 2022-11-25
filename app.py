from flask import Flask, request
import requests
from dotenv import load_dotenv
import os
from os.path import join, dirname
from yookassa import Configuration, Payment
import json


app = Flask(__name__)

def create_invoice(chat_id):
    Configuration.account_id = get_from_env("SHOP_ID")
    Configuration.secret_key = get_from_env("PAYMENT_TOKEN")

    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://19104406-900177.renderforestsites.com/"
        },
        "capture": True,
        "description": "Заказ №37",
        "metadata": {"chat_id": chat_id}
    })

    return payment.confirmation.confirmation_url
def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key) # возвращает секретный токен

def send_message(chat_id, text):
    method = "sendMessage"
    token = get_from_env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def send_pay_button(chat_id, text):
    invoice_url = create_invoice(chat_id)

    method = "sendMessage"
    token = get_from_env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"

    data = {"chat_id": chat_id, "text": text, "reply_markup": json.dumps({"inline_keyboard": [[{
        "text": "Оплатить!",
        "url": f"{invoice_url}"
    }]]})}
    requests.post(url, data=data)

def chek_if_succesful_payment(request):
    try:
        if request.json["event"] == "payment.succeeded":
            return True
    except KeyError:
        return False

    return False

@app.route('/', methods=["POST"]) # localhost:5000/ - на этот адресс телега шлет сообщения
def process():  # put application's code here
    if chek_if_succesful_payment(request):
        # Обработка запросов от Юкасса
        chat_id = request.json["object"]["metadata"]["chat_id"]
        send_message(chat_id, "Отдуши, ей богу")
    else:
        # Обработка запросов от Телеграм
   # print(request.json)
        chat_id = request.json["message"]["chat"]["id"]
        send_pay_button(chat_id=chat_id, text="Закинь деняк, бро..плиз(П.С. для оплаты используй карту 5555 5555 5555 4444 любой месяц и год и любой CVV код, после оплаты не забудь надать на кнопку 'вернуться на сайт' :)")
    return {"ok": True}


if __name__ == '__main__':
    app.run()

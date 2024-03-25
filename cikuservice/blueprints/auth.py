from datetime import datetime
from flask import Blueprint, render_template, abort, request, redirect
from flask import url_for, make_response
from core.flask import session, cross_origin
from core.validation import Validation
import json


auth = Blueprint('auth', __name__)


def user_valid(valid: Validation, user: str, password: str) -> bool:
    if user == "firasrafislam@live.com":
        return True
    else:
        return False


@auth.route("/")
def index():
    return render_template("index.html")


@auth.route("/login")
def login_GET():
    return_to = request.args.get('return_to')
    context = session.get("login_context")
    return render_template("login.html",
                           return_to=return_to,
                           login_context=context)


@auth.route("/register")
def register():
    return render_template("registration.html")


@auth.route("/register/step2", methods=["POST"])
def register_POST():
    valid = Validation(request)
    body = '<p>Register successful</p>'
    return make_response(body)


@auth.route("/signup")
def signup():
    return render_template("register-step2.html")


@auth.route("/api/signup", methods=["POST"])
def signup_POST():
    body = '<p>Created Account Successful</p>'
    bodyError = '<p>Body Error</p>'
    valid = Validation(request)
    username = valid.require("username", friendly_name="Username")
    email = valid.require("email", friendly_name="Email address")
    password = valid.require("password", friendly_name="Password")

    if not valid.ok:
        return make_response(bodyError), 400


    return make_response(body)


@auth.route("/help")
def help_GET():
    return render_template("help.html")


@auth.route("/api/login", methods=["POST"])
def login_POST():
    valid = Validation(request)
    print("Check validation")
    username = valid.require("username", friendly_name="Username")
    password = valid.require("password", friendly_name="Password")
    return_to = valid.optional("return_to", "/")

    if not valid.ok:
        print("Valid not ok")
        return make_response(valid.summary())

    if not user_valid(valid, username, password):
        print("User not valid")
        return make_response(valid.summary())

    body = "Hola Mundo!"
    response = make_response(body)
    response.headers["HX-Push-URL"] = "false"
    trigger_string = json.dumps({"event1":"A message", "event2":"Another message"})
    response.headers["HX-Trigger"] = trigger_string

    print("Logged in account")
    return response

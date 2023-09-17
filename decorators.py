import functools
from flask import g, redirect, flash

def login_required(func):
    @functools.wraps(func)
    def wrapper_login_required(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized. Requires log-in.", "danger")
            return redirect("/")
        return func(*args, **kwargs)

    return wrapper_login_required
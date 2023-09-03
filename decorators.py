import functools
from flask import g, redirect, flash

def check_user(func):
    @functools.wraps(func)
    def wrapper_check_user(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper_check_user
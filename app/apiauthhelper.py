from functools import wraps # functools is a built-in Python package. wraps is a built-in python function that will help us build wrappers
from flask import request, jsonify # will be using some json information so we'll have to work with json/jsonify

from app.models import User

# here we are creating the @token_required decorator for protecting our API routes

def token_required(func): # token_required is the overarching function we have access to, and the function inside of it (that it takes in) is a callback function 
    @wraps(func) # using @wraps allows the function we are passing in to be wrapped in our token_required function
    def decorated(*args, **kwargs): # adding *args and **kwargs because we don't know what kind of arguments will be passed in, so we are allowing all types and an infinite amount
        token = None
        if 'x-access-token' in request.headers: # request is res from our api Login.js file, headers is a key value in the dictionary we are assigning to res, and we are looking to see if it has an x-access-token
            token = request.headers['x-access-token']
        else: # the else is if the header does not exist
            return {
                'status': 'not ok',
                'message': "Missing Header. Please add 'x-access-token' to your Headers."
            }
        if not token: # if it exists, but the value is null (ie, there is no token, so token returns False), return status: not ok
            return {
                'status': 'not ok',
                'message': "Missing Auth Token. Please log in to a user that has a valid token."
            }
        user = User.query.filter_by(apitoken=token).first() # they sent us a token, so we can check the token against what we have in our database
        if not user: # if they typed in a token, but it doesn't belong to anyone, the user variable we assigned above will be False
            return {
                'status': 'not ok',
                'message': 'That token does not belong to a valid user.'
            }
        return func(user=user, *args, **kwargs) # if all of the above checks have passed, we will then run the function because we have confirmed that the user is correct and has a valid token. 
    return decorated
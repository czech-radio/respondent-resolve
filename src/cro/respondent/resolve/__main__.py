#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from flask_restful import Resource,Api

# from cro.respondent.resolve import respondent

import pandas as pd

class HelloWorld(Resource):
        def get(self):
            return {'hello': 'world'}



def main():
    """
    The main application function.
    """

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(HelloWorld,'/')
    
    app.run(debug=True)


if __name__ == '__main__':
    main()

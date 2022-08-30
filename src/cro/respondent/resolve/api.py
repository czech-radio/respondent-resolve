# -*- coding: utf-8 -*-


from flask import Flask
from flask_restful import Resource, Api


class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}


class Server():
   def __init__(self) -> None:
    self.app = Flask(__name__)
    self.api = Api(self.app)

    self.api.add_resource(HelloWorld, "/")

   def run(self):
     self.app.run(debug=True)


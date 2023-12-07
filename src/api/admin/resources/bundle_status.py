import json
import io
import tarfile
import gzip

from flask import request, jsonify, Response
from flask_restx import Resource
from src.extension import api, policy_enforcer_storage

class BundleStatus(Resource):

    @api.doc()
    def post(self):
        print("okok11111111", request.headers)
        return {}, 200
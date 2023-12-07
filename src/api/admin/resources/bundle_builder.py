import json
import os
import io
import tarfile
import gzip

from flask import request, jsonify, Response
from flask_restx import Resource
from src.extension import api, policy_enforcer_storage
from src.helper.helper import combine_data
from src.repository import load_resources_setting, load_user_role_mappings, \
    get_current_resources, get_current_user_role_mappings

script_directory = os.path.dirname(os.path.abspath(__file__))

class BundleBuilder(Resource):

    @api.doc()
    def get(self):
        # if 'Authorization' not in request.headers:
        #     return jsonify({'error': 'Authorization header is missing'}), 401
        #
        # auth_header = request.headers.get('Authorization')
        #
        # if not auth_header.startswith('Bearer '):
        #     return jsonify({'error': 'Invalid Authorization header'}), 401
        # token = auth_header[len('Bearer '):]
        # if token != "bGFza2RqZmxha3NkamZsa2Fqc2Rsa2ZqYWtsc2RqZmtramRmYWxkc2tm":
        #     return jsonify({'error': 'Invalid Authorization header'}), 401
        resources = get_current_resources()
        list_resource_id = set()
        for resource in resources:
            list_resource_id.add(resource[0])
        resource_data = load_resources_setting(list_resource_id)
        user_role_data = get_current_user_role_mappings()
        user_role_mapping = load_user_role_mappings(user_role_data)

        bundle_data = combine_data(resource_data, user_role_mapping)

        with io.BytesIO() as tar_buffer:
            with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
                rego_file_path = os.path.join(script_directory, 'policy.rego')
                print("okokokokokok123",rego_file_path)
                # Add a file to the archive with the JSON data
                info = tarfile.TarInfo('data.json')
                info.size = len(bundle_data)
                tar.addfile(info,
                            fileobj=io.BytesIO(bundle_data.encode('utf-8')))

                tar.add(rego_file_path, arcname="policy.rego")

            # Compress the tar archive using gzip
            tar_buffer.seek(0)
            with io.BytesIO() as gzipped_buffer:
                with gzip.GzipFile(fileobj=gzipped_buffer,
                                   mode='wb') as gzipped:
                    gzipped.write(tar_buffer.read())

                gzipped_buffer.seek(0)

                response = Response(gzipped_buffer.read(),
                                    content_type='application/gzip')
                response.headers[
                    'Content-Disposition'] = 'attachment; filename=output.tar.gz'

        return response

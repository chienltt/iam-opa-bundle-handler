import fnmatch
import json
from collections import Counter

import jwt

from src.extension import policy_enforcer_storage


def match_path(input_path, pattern):
    input_path = input_path.strip('/')
    pattern = pattern.strip('/')

    return fnmatch.fnmatch(input_path, pattern)


def is_subarray(arr1, arr2):
    counter1 = Counter(arr1)
    counter2 = Counter(arr2)

    for element, count in counter1.items():
        if count > counter2[element]:
            return False

    return True


def convert_string_to_set(str):
    str = str.replace('"', '')
    elements = str[1:-1].split(',')

    # Create a set from the elements
    converted_set = set(element.strip() for element in elements)
    return converted_set


def verify_token_signature(token, public_key_json):
    public_key = public_key_json["publicKey"]
    public_key_pem = (
        f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC "
        f"KEY-----")
    algorithm = public_key_json["algorithm"]
    decoded_token = jwt.decode(token, public_key_pem,
                               algorithms=[algorithm],
                               options={"verify_aud": False})
    return decoded_token


def combine_data(resources_datas, user_role_mappings):
    list_clients_id = resources_datas.keys()
    policy_enforcers = dict()
    result = dict()
    for client_id in list_clients_id:
        policy_enforcers[client_id] = policy_enforcer_storage.get(client_id)

    for client_id in list_clients_id:
        result['resource_data'] = dict()
        result['resource_data'][client_id] = dict()
        result['resource_data'][client_id]["policies"] = []
        resources_data = resources_datas[client_id]
        policy_enforcer = policy_enforcers[client_id]
        print("okok0",policy_enforcer)
        match_resource_setting = None
        for policy_enforcer_setting in policy_enforcer['paths']:
            print("okok001",policy_enforcer_setting)
            result_policy = dict()
            result_policy["path"] = policy_enforcer_setting["path"]
            result_policy['method_role_mapping'] = dict()
            for re in resources_data["resources"]:
                for _uri in re['uris']:
                    if match_path(policy_enforcer_setting["path"], _uri):
                        match_resource_setting = re
            if match_resource_setting is not None:
                for method in policy_enforcer_setting["methods"]:
                    scopes = method['scopes']
                    role_policies_require = set()
                    for scope in scopes:
                        for policy in resources_data["policies"]:
                            if policy["type"] == "scope":
                                if scope in policy['config']['scopes']:
                                    apply_policies = convert_string_to_set(
                                        policy['config'][
                                            'applyPolicies'])
                                    role_policies_require.update(apply_policies)
                    roles_require = set()
                    for role_policy in role_policies_require:
                        for policy in resources_data["policies"]:
                            if role_policy == policy['name']:
                                roles = json.loads(policy['config']['roles'])
                                for role in roles:
                                    roles_require.add(role['id'])
                    result_policy['method_role_mapping'][method['method']] = (
                        list(roles_require))
            result['resource_data'][client_id]["policies"].append(result_policy)
    print("okok1111111",result)
    for key in user_role_mappings.keys():
        user_role_mappings[key] = json.loads(user_role_mappings[key])
    result["user_role_mapping"] = user_role_mappings
    print("okok123", json.dumps(result))
    return json.dumps(result)

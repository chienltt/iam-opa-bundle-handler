from flask_restx import Namespace

from src.api.admin.resources.bundle_builder import BundleBuilder
from src.api.admin.resources.policy_enforcer import PolicyEnforcer
from src.api.admin.resources.test import LoadDataResource

_ROUTES = [
    {
        'name': 'Bundle Builder',
        'description': 'Bundle Builder',
        'path': '/bundle',
        'resources': [
            (BundleBuilder, '/')
        ]
    },
    {
        'name': 'Policy enforcer',
        'description': 'Policy enforcer',
        'path': '/policy-enforcer',
        'resources': [
            (PolicyEnforcer, '/<client_id>')
        ]
    },
]


def _add_namespaces():
    """Add namespaces and resources for api instance of the version 1.0."""
    for ns in _ROUTES:
        resources = ns.pop('resources', [])
        api_ns = Namespace(**ns)
        for rs in resources:
            api_ns.add_resource(*rs)
        yield api_ns


ADMIN_API_ROUTES = _add_namespaces()
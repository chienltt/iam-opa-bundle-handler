
package policy

import input
import data

default allow = false

allow {
    roles = data.user_role_mapping[input.user_id]

    policies = data.resource_data[input.client_id].policies

    policy := policies[policy_index]

    policy.method_role_mapping[input.method]

    required_roles := policy.method_role_mapping[input.method]

    set_roles := {x | x := roles[_]}

    set_required_roles := {x | x:= required_roles[_]}

    common := set_roles & set_required_roles

    count(common) > 0
}

policy_index = i {
    policies = data.resource_data[input.client_id].policies
    glob.match(policies[i].path,[],input.path)
}
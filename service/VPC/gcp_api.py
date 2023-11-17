from google.oauth2 import service_account
from googleapiclient import discovery
import requests
from google.auth.transport.requests import Request
from google.cloud import compute_v1


# Replace with your GCP project ID
project_id = 'mhrt-dev3-389609'
region = 'us-central1'
# Load your service account key file
service_account_file = 'gcpkey.json'

# Authenticate with your service account key
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=[
        'https://www.googleapis.com/auth/cloud-platform']
)
# credentials.refresh(Request())
# headers = {'Authorization': f'Bearer {credentials.token}'}
# endpoint_location = "https://compute.googleapis.com/compute/v1/locations/global/firewallPolicies"
# response_location = requests.get(endpoint_location, headers=headers)
# print(response_location)


def get_details_firewall_policy_rule(project_id):
    compute_client = compute_v1.NetworkFirewallPoliciesClient()
    firewalls_policies = compute_client.list(project=project_id)
    list_policy_firewall = []

    dic_policy_rule = {}
    for firewalls_policy in firewalls_policies:
        # Use dir() to get all attributes and print their values
        policy_name = firewalls_policy.name
        list_rule_policy = []
        # print(firewalls_policy.rules[0].)
        for firewall in firewalls_policy.rules:
            details = []
            fire_priority = firewall.priority
            if firewall.description:
                fire_description = firewall.description
            else:
                fire_description = "-"
            fire_direction = firewall.direction
            if firewall.target_service_accounts:
                fire_tagrget = f'Service account: {firewall.target_service_accounts}'
            elif firewall.target_secure_tags:
                fire_tagrget = f'target_secure_tags: {firewall.target_secure_tags}'
            elif firewall.target_resources:
                fire_tagrget = f'target_resources: {firewall.target_resources}'
            else:
                fire_tagrget = 'Apply to all'

            if firewall.match.src_address_groups or firewall.match.src_fqdns or firewall.match.src_ip_ranges or firewall.match.src_region_codes or firewall.match.src_secure_tags or firewall.match.src_threat_intelligences:
                fire_source = f'IP ranges: {firewall.match.src_ip_ranges} - FQDN: {firewall.match.src_fqdns} - Geolocations: {firewall.match.src_region_codes} - Google Cloud Threat Intelligence: {firewall.match.src_threat_intelligences} - src_address_groups:{firewall.match.src_address_groups} - src_secure_tags: {firewall.match.src_secure_tags}'
            else:
                fire_source = "-"
            if firewall.match.dest_address_groups or firewall.match.dest_fqdns or firewall.match.dest_ip_ranges or firewall.match.dest_region_codes or firewall.match.dest_threat_intelligences:
                fire_dest = f'IP ranges: {firewall.match.dest_ip_ranges} - FQDN: {firewall.match.dest_fqdns} - Geolocations: {firewall.match.dest_region_codes} - Google Cloud Threat Intelligence: {firewall.match.dest_threat_intelligences} - dest_address_groups:{firewall.match.dest_address_groups}'
            else:
                fire_dest = "-"          
                  
            fire_list_pp = []
            for protocol in firewall.match.layer4_configs:
                pro = ""
                port = ""
                if protocol.ip_protocol:
                    pro = protocol.ip_protocol
                if protocol.ports:
                    port = f':{protocol.ports}'

                fire_list_pp.append(f'{pro}{port}')
            
            fire_action = firewall.action
            details = [fire_priority, fire_description, fire_direction, fire_tagrget, fire_source, fire_dest, fire_list_pp, fire_action]
            list_rule_policy.append(details)
        dic_policy_rule[policy_name] = list_rule_policy 
    return dic_policy_rule


print(get_details_firewall_policy_rule(project_id))

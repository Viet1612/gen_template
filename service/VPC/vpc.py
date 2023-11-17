from google.cloud import compute_v1
import os
import sys
import openpyxl
from google.oauth2 import service_account
from googleapiclient import discovery
import requests
from google.cloud import vpcaccess_v1
from google.auth.transport.requests import Request
# import module excel
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
grandparent_folder_path = os.path.dirname(parent)
commom_path = os.path.join(grandparent_folder_path, "common")
sys.path.append(commom_path)
import excel_common

DataConfig = excel_common.getConfig(current + '/vpc-parameter.json')
project_id = DataConfig['project_id']
gcp_key = DataConfig['GCPKEY']


service_account_file = os.path.join(commom_path, gcp_key)

credential_path = service_account_file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
# Authenticate with your service account key
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=[
        'https://www.googleapis.com/auth/cloud-platform']
)


def get_vpc_details(project_id: str):
    list_vpc_details = []
    vpc_client = compute_v1.NetworksClient()
    vpcs_list = vpc_client.list(project=project_id)

    for vpc in vpcs_list:
        vpc_id = vpc.id
        vpc_name = vpc.name
        vpc_mtu = vpc.mtu
        if vpc.internal_ipv6_range:
            vpc_ula_ipv6 = vpc.internal_ipv6_range
        else:
            vpc_ula_ipv6 = "-"
        print(vpc.internal_ipv6_range)
        if vpc.auto_create_subnetworks:
            vpc_subnet_mode = "Auto subnets"
        else:
            vpc_subnet_mode = "Custom subnets"
        if vpc.routing_config.routing_mode == "REGIONAL":
            vpc_routing_mode = "Regional"
        else:
            vpc_routing_mode = "Global"
        vpc_dns_policy = get_DNS_server_policy(project_id, vpc_name)
        if vpc_dns_policy == False:
            vpc_dns_policy = "-"

        detail = [vpc_id, vpc_name, vpc_mtu, vpc_ula_ipv6,
                  vpc_subnet_mode, vpc_routing_mode, vpc_dns_policy]
        list_vpc_details.append(detail)

    return list_vpc_details


def get_DNS_server_policy(project_id, vpc_name):
    dns = discovery.build('dns', 'v1', credentials=credentials)
    policies = dns.policies().list(project=project_id).execute()
    for policy in policies.get('policies', []):
        networks = policy['networks']
        for network in networks:
            if vpc_name in network['networkUrl']:
                return policy['name']
            else:
                continue
    return False

# Subnet
def get_subnet_details(project_id, list_vpc_details):
    client = compute_v1.SubnetworksClient()
    request = compute_v1.AggregatedListSubnetworksRequest(
        project=project_id,
    )
    list_subnets = client.aggregated_list(request=request)
    list_subnet_detail = []
    for subnet in list_subnets:
        sub_region = ((subnet[0]).split('/'))[-1]
        for sub in subnet[1].subnetworks:
            detail_subnet = []
            subnet_id = sub.id
            subnet_name = sub.name
            subnet_vpc = ((sub.network).split('/'))[-1]
            subnet_region = sub_region
            subnet_ip_stack_type = sub.stack_type
            if sub.ip_cidr_range:
                subnet_internal_ip = sub.ip_cidr_range
            else:
                subnet_internal_ip = '-'
            if sub.external_ipv6_prefix:
                subnet_external_ip = sub.external_ipv6_prefix
            else:
                subnet_external_ip = '-'
            if sub.secondary_ip_ranges:
                subnet_secondary_ip_ranges = sub.secondary_ip_ranges[0].ip_cidr_range
            else:
                subnet_secondary_ip_ranges = '-'
            if sub.gateway_address:
                subnet_gateway = sub.gateway_address
            else:
                subnet_gateway = '-'
            if sub.internal_ipv6_prefix:
                subnet_internal_ipv6_range = sub.internal_ipv6_prefix
            else:
                subnet_internal_ipv6_range = '-'
            if sub.private_ip_google_access == True:
                subnet_private_google_access = 'On'
            else:
                subnet_private_google_access = 'Off'
            if sub.enable_flow_logs == True:
                subnet_flow_logs = 'On'
            else:
                subnet_flow_logs = 'Off'
            detail_subnet = [subnet_id, subnet_name, subnet_vpc, subnet_region, subnet_ip_stack_type, subnet_internal_ip, subnet_external_ip,
                             subnet_secondary_ip_ranges, subnet_gateway, subnet_internal_ipv6_range, subnet_private_google_access, subnet_flow_logs]
            list_subnet_detail.append(detail_subnet)
    dic_subnet_vpc_detail = {}
    for vpc in list_vpc_details:
        vpc_name = vpc[1]
        # nhớ xóa cái này
        # if vpc_name == 'default':
        #     continue
        list_sub_in_vpc = []
        for subnet in list_subnet_detail:
            if subnet[2] == vpc_name:
                list_sub_in_vpc.append(subnet)
        dic_subnet_vpc_detail[vpc_name] = list_sub_in_vpc

    return dic_subnet_vpc_detail

# deatail route
def get_details_routes(project_id, list_vpc_details):
    list_routes_details = []
    client = compute_v1.RoutesClient()
    request = compute_v1.ListRoutesRequest(
        project=project_id,
    )
    list_routes = client.list(request=request)
    for route in list_routes:
        details = []
        rou_id = route.id
        rou_name = route.name
        rou_vpc = ((route.network).split('/'))[-1]
        if route.description:
            rou_des = route.description
        else:
            rou_des = "-"
        # Cái type này bị ngu xem lại
        if route.route_type:
            rou_type = "Policy-based"
        else:
            rou_type = "Static"
        # -----------------------#
        rou_dest_range = route.dest_range
        if ':' in rou_dest_range:
            rou_ip_version = "IPv6"
        else:
            rou_ip_version = "IPv4"
        rou_priority = route.priority
        if route.tags:
            rou_instance_tags = route.tags
        else:
            rou_instance_tags = "This route applies to all instances within the specified network"
        if route.next_hop_gateway:
            rou_next_hop = ((route.next_hop_gateway).split('/'))[-1]
        elif route.next_hop_hub:
            rou_next_hop = route.next_hop_hub
        elif route.next_hop_ilb:
            rou_next_hop = route.next_hop_ilb
        elif route.next_hop_instance:
            next_hop = route.next_hop_instance.split('/')
            rou_next_hop = f'{next_hop[-1]} (Zone {next_hop[-3]})'
        elif route.next_hop_ip:
            rou_next_hop = route.next_hop_ip
        elif route.next_hop_network:
            vpc_network = ((route.next_hop_network).split('/'))[-1]
            rou_next_hop = f'vpc: {vpc_network}'
        elif route.next_hop_peering:
            rou_next_hop = route.next_hop_peering
        elif route.next_hop_vpn_tunnel:
            rou_next_hop = route.next_hop_vpn_tunnel
        # check cái này sau
        rou_apply_instance = 'Please refer to GCP console'
        # -----------------------#
        details = [rou_id, rou_name, rou_vpc, rou_des, rou_type, rou_ip_version,
                   rou_dest_range, rou_priority, rou_instance_tags, rou_next_hop, rou_apply_instance]
        list_routes_details.append(details)

    dic_routes_detail = {}
    for vpc in list_vpc_details:
        vpc_name = vpc[1]
        list_rou_in_vpc = []
        for route in list_routes_details:
            if vpc_name in route[2]:
                list_rou_in_vpc.append(route)
        dic_routes_detail[vpc_name] = list_rou_in_vpc
    return dic_routes_detail

# detail firewall_rule
def get_details_firewalls_rule(project_id, list_vpc_details):
    compute_client = compute_v1.FirewallsClient()
    firewalls = compute_client.list(project=project_id)
    list_details_firewalls = []
    for firewall in firewalls:
        details = []
        fire_id = firewall.id
        fire_name = firewall.name
        fire_vpc = ((firewall.network).split('/'))[-1]
        if firewall.description:
            fire_description = firewall.description
        else:
            fire_description = "-"
        fire_type = firewall.direction
        if firewall.target_service_accounts:
            fire_tagrget = f'Service account: {firewall.target_service_accounts}'
        elif firewall.target_tags:
            fire_tagrget = f'Target tags: {firewall.target_tags}'
        else:
            fire_tagrget = 'All instances in the network'
        if firewall.source_ranges or firewall.source_service_accounts or firewall.source_tags:
            fire_filters = f'IP ranges: {firewall.source_ranges} - Service account: {firewall.source_service_accounts} - Tags: {firewall.source_tags}'
        if firewall.allowed:
            fire_pro_port = firewall.allowed
            fire_action = "Allow"
        elif firewall.denied:
            fire_pro_port = firewall.denied
            fire_action = "Deny"
        fire_list_pp = []
        for protocol in fire_pro_port:
            pro = ""
            port = ""
            if protocol.I_p_protocol:
                pro = protocol.I_p_protocol
            if protocol.ports:
                port = f'/{protocol.ports}'

            fire_list_pp.append(f'{pro}{port}')
        fire_priority = firewall.priority
        if firewall.log_config.enable == False:
            fire_log = "Off"
        if firewall.log_config.enable == True:
            fire_log = "On"
        if firewall.disabled == False:
            fire_enforcement = "Enabled"
        if firewall.disabled == True:
            fire_enforcement = "Disabled"
        # check cái này sau
        fire_apply_instance = 'Please refer to GCP console'
        details = [fire_id, fire_name, fire_vpc, fire_description, fire_type, fire_tagrget, fire_filters,
                   fire_list_pp, fire_action, fire_priority, fire_log, fire_enforcement, fire_apply_instance]
        list_details_firewalls.append(details)

    dic_firewalls_detail = {}
    for vpc in list_vpc_details:
        vpc_name = vpc[1]
        list_fire_in_vpc = []
        for fire in list_details_firewalls:
            if vpc_name in fire[2]:
                list_fire_in_vpc.append(fire)
        dic_firewalls_detail[vpc_name] = list_fire_in_vpc
    return dic_firewalls_detail

# firewall_policy
def get_details_firewall_policy(project_id, sheet_name_rule):
    compute_client = compute_v1.NetworkFirewallPoliciesClient()
    firewalls_policy = compute_client.list(project=project_id)
    list_policy_firewall = []
    for policy in firewalls_policy:
        details = []
        policy_id = policy.id
        policy_name = policy.name
        if policy.description:
            policy_description = policy.description
        else:
            policy_description = "-"
        policy_rule = f'Please check sheet [{sheet_name_rule}]'
        policy_scope = "Global"
        policy_list_associated = []
        if len(policy.associations) > 0:
            for vpc in policy.associations:
                policy_list_associated.append(((vpc.name).split('/'))[-1])
        details = [policy_id, policy_name, policy_description,
                   policy_rule, policy_scope, policy_list_associated]
        list_policy_firewall.append(details)
    return list_policy_firewall

# get detail ip
def get_detail_ip_static(project_id):
    pass
    client = compute_v1.AddressesClient()
    request = compute_v1.AggregatedListAddressesRequest(
        project=project_id,
    )
    list_ips = client.aggregated_list(request=request)
    list_detail_ip = []
    for ips in list_ips:
        ip_region = ((ips[0]).split('/'))[-1]
        if ips[1].addresses:
            for ip in ips[1].addresses:
                details = []
                ip_address = ip.address
                ip_name = ip.name
                if ip.network:
                    ip_vpc = ((ip.network).split('/'))[-1]
                else:
                    ip_vpc = "-"
                if ip.subnetwork:
                    ip_subnet = ((ip.subnetwork).split('/'))[-1]
                else:
                    ip_subnet = "-"
                ip_type = "Static"
                if ip.ip_version:
                    ip_version = ip.ip_version
                else:
                    if ':' in ip.address:
                        ip_version = "IPv6"
                    else:
                        ip_version = "IPv4"
                ip_user = []
                if ip.users:
                    for user in ip.users:
                        ip_user.append((str(user).split('/'))[-1])
                else:
                    ip_user = ["None"]
                ip_access_type = ip.address_type
                ip_network_tier = ip.network_tier
                ip_labels = 'Please refer to GCP console'
                details = [ip_address, ip_name, ip_vpc, ip_subnet, ip_region, ip_type,
                           ip_version, ip_user, ip_access_type, ip_network_tier, ip_labels]
                list_detail_ip.append(details)

    dic_ip_detail = {}
    list_access_type = ['INTERNAL', 'EXTERNAL']
    for type in list_access_type:
        list_ip_for_type = []
        for ip in list_detail_ip:
            if type in ip[8]:
                list_ip_for_type.append(ip)
        dic_ip_detail[type] = list_ip_for_type
    return dic_ip_detail

# get detail peering
def get_detail_vpc_peering(project_id):
    service = discovery.build('compute', 'v1', credentials=credentials)
    request = service.networks().list(project=project_id)
    networks = request.execute()
    dic_vpc_peering = {}
    for network in networks['items']:
        network_name = network['name']
        peerings = network.get('peerings', [])
        list_peering_detail = []
        if len(peerings) > 0:
            for peer in peerings:
                details = []
                if peer['name']:
                    peer_name = peer['name']
                else:
                    peer_name = "-"
                if peer['network']:
                    peer_peered_vpc = (str(peer['network']).split('/'))[-1]
                    peer_project_id = (str(peer['network']).split('/'))[-4]
                else:
                    peer_peered_vpc = "-"
                    peer_project_id = "-"
                if peer['stackType']:
                    peer_stack_type = peer['stackType']
                else:
                    peer_stack_type = "-"
                importCustomRoutes = peer['importCustomRoutes']
                exportCustomRoutes = peer['exportCustomRoutes']
                if importCustomRoutes or exportCustomRoutes:
                    if importCustomRoutes and exportCustomRoutes:
                        peer_custom_route = "Import & Export custom routes"
                    elif importCustomRoutes:
                        peer_custom_route = "Import custom routes"
                    elif exportCustomRoutes:
                        peer_custom_route = "Export custom routes"
                else:
                    peer_custom_route = "None"
                    
                importSubnetRoutesWithPublicIp = peer['importSubnetRoutesWithPublicIp']
                exportSubnetRoutesWithPublicIp = peer['exportSubnetRoutesWithPublicIp']
                if importSubnetRoutesWithPublicIp or exportSubnetRoutesWithPublicIp:
                    if importSubnetRoutesWithPublicIp and exportSubnetRoutesWithPublicIp:
                        peer_subnet_route = "Import & Export subnet routes with public IP"
                    elif importSubnetRoutesWithPublicIp:
                        peer_subnet_route = "Import subnet routes with public IP"
                    elif exportSubnetRoutesWithPublicIp:
                        peer_subnet_route = "Export subnet routes with public IP"
                else:
                    peer_subnet_route = "None"
                peer_status = peer['state']
                peer_im_ex_route = "Please refer to GCP console"
                details = [peer_name, network_name, peer_peered_vpc, peer_project_id, peer_stack_type, peer_custom_route, peer_subnet_route, peer_status, peer_im_ex_route]
                list_peering_detail.append(details)
        dic_vpc_peering[network_name] = list_peering_detail
        
    return dic_vpc_peering
                

# get get_detail_serverless_vpc
def get_detail_serverless_vpc(project_id):
    credentials.refresh(Request())
    headers = {'Authorization': f'Bearer {credentials.token}'}
    endpoint_location = f'https://vpcaccess.googleapis.com/v1/projects/{project_id}/locations'
    response_location = requests.get(endpoint_location, headers=headers)
    list_detail_serverless_vpc = []
    for location in response_location.json()['locations']: 
        location_id = location['locationId']
        client = vpcaccess_v1.VpcAccessServiceClient()
        parent = f'projects/{project_id}/locations/{location_id}'
        request = vpcaccess_v1.ListConnectorsRequest(
            parent=parent,
        )
        connectors = client.list_connectors(request=request)
        for connector in connectors:
            if connector:
                details = []
                con_name = (str(connector.name).split('/'))[-1]
                con_network = connector.network
                con_state = connector.state
                if connector.subnet:
                    con_subnet = connector.subnet
                else:
                    con_subnet = '-'
                con_ipCidrRange = connector.ip_cidr_range
                con_minInstances = connector.min_instances
                con_maxInstances = connector.max_instances
                con_machineType = connector.machine_type
                con_activeInstance = "Please refer to GCP console"
                details = [con_name, con_network, location_id, con_state, con_subnet, con_ipCidrRange, con_minInstances, con_maxInstances, con_machineType, con_activeInstance]
                list_detail_serverless_vpc.append(details)
    return list_detail_serverless_vpc
 

#get rule fire policy
def get_details_firewall_policy_rule(project_id):
    compute_client = compute_v1.NetworkFirewallPoliciesClient()
    firewalls_policies = compute_client.list(project=project_id)
    dic_policy_rule = {}
    for firewalls_policy in firewalls_policies:
        policy_name = firewalls_policy.name
        list_rule_policy = []
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


# insert detail
def insert_vertical_detail_for_vpc_to_excel(ws, dic_detail, rowStart, leng, row_range, startColumn, text, note_move_start, note_move_end, isCopyNote):
    count = len(dic_detail)
    rowEnd = rowStart + row_range
    # copy sang ngang
    if count > 1 and isCopyNote:
        ws.move_range(note_move_start + str(rowStart) + note_move_end + str(rowEnd), rows=0,
                      cols=leng * (count - 1))
        for i in range(1, count):
            excel_common.insertAndCopyColumns(
                ws, rowStart, rowEnd, startColumn, leng, i)
    max_length = 0
    for route in dic_detail:
        if len(dic_detail[route]) > max_length:
            max_length = len(dic_detail[route])
    print(max_length)
    endNumber = max_length*row_range + rowStart
    # copy xuong duoi
    excel_common.insertAndCopyRowRangeWithText(
        ws, max_length, row_range, rowEnd + 1, text, 2, 2)

    # fill data

    i = 0
    for detail in dic_detail:
        j = 0
        for detail in dic_detail[detail]:
            excel_common.fillData(ws, rowStart + 2 + j *
                                  row_range, startColumn + i*leng, detail)
            j = j + 1
        i = i + 1
    return endNumber


def insert_horizontal_info_to_excel(ws, list_details, rowStart, row_range, startColumn, leng):
    count_list = len(list_details)
    rowEnd = rowStart + row_range
    if count_list > 1:
        ws.move_range("AF" + str(rowStart) + ":AT" + str(rowEnd), rows=0,
                      cols=leng * (count_list - 1))
        for i in range(1, count_list):
            excel_common.insertAndCopyColumns(
                ws, rowStart, rowEnd, startColumn, leng, i)
        i = 0
    for info in list_details:
        excel_common.fillData(ws, rowStart + 1, startColumn + i*leng, info)
        i = i + 1
    return rowStart + row_range


if __name__ == '__main__':
    fileInputTemplate = DataConfig['FileInputTemplate']
    fileOutputTemplate = DataConfig['FileOutputTemplate']
    fileInputTemplate_folder = os.path.join(grandparent_folder_path, "input")
    fileInputTemplate_path = os.path.join(
        fileInputTemplate_folder, fileInputTemplate)
    fileOutputTemplate_folder = os.path.join(grandparent_folder_path, "output")
    fileOutputTemplate_path = os.path.join(
        fileOutputTemplate_folder, fileOutputTemplate)

    wb = openpyxl.load_workbook(fileInputTemplate_path)
    worksheet = format(DataConfig['WorkSheet'])
    ws = wb[worksheet]

    # VPC
    list_vpc_details = get_vpc_details(project_id)
    endVPC = insert_horizontal_info_to_excel(ws, list_vpc_details, 6, 7, 17, 15)

    # Subnet
    dic_subnet_vpc_detail = get_subnet_details(project_id, list_vpc_details)
    endNumberSubnet = insert_vertical_detail_for_vpc_to_excel(
        ws, dic_subnet_vpc_detail, endVPC + 3, 15, 13, 17, "Subnet #", "AF", ":AT", True)

    # Route
    dic_routes_detail = get_details_routes(project_id, list_vpc_details)
    endNumberSubnetRoute = insert_vertical_detail_for_vpc_to_excel(
        ws, dic_routes_detail, endNumberSubnet + 3, 15, 12, 17, "Route #", "AF", ":AT", True)
    
    #vpc peering
    dic_vpc_peering = get_detail_vpc_peering(project_id)
    endNumberPeering = insert_vertical_detail_for_vpc_to_excel (ws, dic_vpc_peering, endNumberSubnetRoute + 3, 15, 10, 17, "Peering #", "AF", ":AT", True)

    # Firewall Rule
    dic_firewalls_rule_detail = get_details_firewalls_rule(
        project_id, list_vpc_details)
    endNumberfireRoute = insert_vertical_detail_for_vpc_to_excel(
        ws, dic_firewalls_rule_detail, endNumberPeering + 4, 15, 14, 17, "Firewall rule #", "AF", ":AT", True)

    # Firewall policy
    list_policy_firewall = get_details_firewall_policy(
        project_id, DataConfig['WorkSheet_Firewall_Policy'])
    endNumberfirePolicy = insert_horizontal_info_to_excel(
        ws, list_policy_firewall, endNumberfireRoute + 3, 6, 17, 15)

    # ip static
    dic_ip_detail = get_detail_ip_static(project_id)
    endNumberIP = insert_vertical_detail_for_vpc_to_excel(
        ws, dic_ip_detail, endNumberfirePolicy + 4, 15, 12, 17, "IP #", "AF", ":AT", False)
   
    
    #serverless vpc
    list_serverless_vpc = get_detail_serverless_vpc(project_id)
    endNumberServerless = insert_horizontal_info_to_excel(ws, list_serverless_vpc, endNumberIP + 3, 10, 17, 15)

    wb.save(fileOutputTemplate_path)
    print(fileInputTemplate)
    wb.close()

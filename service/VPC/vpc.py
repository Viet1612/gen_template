
from google.cloud import compute_v1
import os
import sys
import openpyxl
from google.oauth2 import service_account
from googleapiclient import discovery
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


def insert_vpc_info_to_excel(ws, list_vpc_details):
    count_vpc = len(list_vpc_details)
    rowPrevious = 0
    leng = 15
    startColumn = 17
    rowStart = 6
    rowEnd = 13
    if count_vpc > 1:
        ws.move_range("AF" + str(6 + rowPrevious) + ":AT" + str(13 + rowPrevious), rows=0,
                      cols=leng * (count_vpc - 1))
        for i in range(1, count_vpc):
            excel_common.insertAndCopyColumns(
                ws, rowStart, rowEnd, startColumn, leng, i)
        i = 0
    for vpc_info in list_vpc_details:
        excel_common.fillData(ws, rowStart + 1, startColumn + i*leng, vpc_info)
        i = i + 1


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

# insert detail subnet
def insert_subnet_to_excel(ws, dic_subnet_vpc_detail, list_vpc_details):
    count_vpc = len(list_vpc_details)
    rowPrevious = 0
    leng = 15
    startColumn = 17
    rowStart = 16
    rowEnd = 29
    row_range = 13
    row_end_1 = 30
    # copy sang ngang
    if count_vpc > 1:
        ws.move_range("AF" + str(rowStart) + ":AT" + str(rowEnd), rows=0,
                      cols=leng * (count_vpc - 1))
        for i in range(1, count_vpc):
            excel_common.insertAndCopyColumns(
                ws, rowStart, rowEnd, startColumn, leng, i)
    max_length = 0
    for subnet in dic_subnet_vpc_detail:
        if len(dic_subnet_vpc_detail[subnet]) > max_length:
            max_length = len(dic_subnet_vpc_detail[subnet])
    print(max_length)
    endNumber = max_length*row_range + rowStart
    # copy xuong duoi
    excel_common.insertAndCopyRowRangeWithText(
        ws, max_length, row_range, row_end_1, "Subnet #", 2, 2)

    # fill data

    i = 0
    for subnets in dic_subnet_vpc_detail:
        j = 0
        for subnet in dic_subnet_vpc_detail[subnets]:
            excel_common.fillData(ws, rowStart + 2 + j *
                                  row_range, startColumn + i*leng, subnet)
            j = j + 1
        i = i + 1
    return endNumber

def get_details_routes(ws, project_id, list_vpc_details):
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
        rou_des = route.description
        # Cái type này bị ngu xem lại
        if route.route_type: 
            rou_type = "Static"
        else:
            rou_type = "Policy-based"
        #-----------------------#
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
        #check cái này sau
        rou_apply_instance = 'Please refer to GCP console'
        #-----------------------#
        details = [rou_id, rou_name, rou_vpc, rou_des, rou_type, rou_ip_version, rou_dest_range, rou_priority, rou_instance_tags, rou_next_hop, rou_apply_instance]
        list_routes_details.append(details)
        
    dic_routes_detail = {}
    for vpc in list_vpc_details:
        vpc_name = vpc[1]
        list_rou_in_vpc = []
        for route in list_routes_details:
            if  vpc_name in route[2]:
                list_rou_in_vpc.append(route)
        dic_routes_detail[vpc_name] = list_rou_in_vpc    
    return dic_routes_detail       

# insert detail route
def insert_route_to_excel(ws, dic_routes_detail, list_vpc_details, end_row_before):
    count_vpc = len(list_vpc_details)
    rowPrevious = end_row_before
    leng = 15
    startColumn = 17
    row_range = 12
    rowStart = rowPrevious + 3
    rowEnd = rowStart + row_range
    row_end_1 = rowEnd + 1
    # copy sang ngang
    if count_vpc > 1:
        ws.move_range("AF" + str(rowStart) + ":AT" + str(rowEnd), rows=0,
                      cols=leng * (count_vpc - 1))
        for i in range(1, count_vpc):
            excel_common.insertAndCopyColumns(
                ws, rowStart, rowEnd, startColumn, leng, i)
    max_length = 0
    for route in dic_routes_detail:
        if len(dic_routes_detail[route]) > max_length:
            max_length = len(dic_routes_detail[route])
    print(max_length)
    endNumber = max_length*row_range + rowStart
    # copy xuong duoi
    excel_common.insertAndCopyRowRangeWithText(
        ws, max_length, row_range, row_end_1, "Route #", 2, 2)

    # fill data

    i = 0
    for routes in dic_routes_detail:
        j = 0
        for routes in dic_routes_detail[routes]:
            excel_common.fillData(ws, rowStart + 2 + j *
                                  row_range, startColumn + i*leng, routes)
            j = j + 1
        i = i + 1
    return endNumber


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

    list_vpc_details = get_vpc_details(project_id)
    dic_subnet_vpc_detail = get_subnet_details(project_id, list_vpc_details)

    insert_vpc_info_to_excel(ws, list_vpc_details)
    endNumberSubnet = insert_subnet_to_excel(
        ws, dic_subnet_vpc_detail, list_vpc_details)
    dic_routes_detail = get_details_routes(ws, project_id, list_vpc_details)
    insert_route_to_excel(ws, dic_routes_detail, list_vpc_details, endNumberSubnet)

    wb.save(fileOutputTemplate_path)
    print(fileInputTemplate)
    wb.close()


# print(get_DNS_server_policy(project, "trung-tf-vpc"))
# print(get_vpc_details(project))

from google.cloud import compute_v1
from google.cloud import vpcaccess_v1
from google.cloud import  resourcemanager
from google.cloud import location

def list_all_subnets(project_id):
    compute_client = compute_v1.NetworkFirewallPoliciesClient()
    firewalls_policy = compute_client.list(project=project_id)
    print(firewalls_policy)
        
def sample_get(project_id):
    # Create a client
    client = vpcaccess_v1.VpcAccessServiceClient()
    
    parent = f'projects/{project_id}'
    request = vpcaccess_v1.ListConnectorsRequest(
        parent=parent,
    )
    
    # Initialize request argument(s)
    locations = client.list_locations(request=request)
    print(locations)
    # Make the request
    # page_result = client.list_connectors(request=request)

    # # Handle the response
    # for response in page_result:
    #     print(response)
   
        
if __name__ == "__main__":
    project_id = "mhrt-dev3-389609"
    list_all_subnets(project_id)
    # sample_aggregated_list(project_id)

    # a=""
    # if a:
    #     print("aaaaa")
    # list_all_subnets(project_id)
    # list_of_lists = [
    # ["key1", "value1", "info1", "extra1"],
    # ["key2", "value2", "info2", "extra2"],
    # ["key3", "value3", "info3", "extra3"],
    # # Thêm các danh sách con khác nếu cần
    # ]

    # # Tạo một từ điển từ danh sách của danh sách
    # dictionary = {item[0]: item[1:] for item in list_of_lists}

    # # print(dictionary)
    # url = "tf-instance-thu2"
    
    # # # Tách chuỗi bằng dấu '/'
    # # url_parts = url.split('/')

    # # # Lấy tên máy ảo và khu vực
    # # machine_name = url_parts[-1]
    # # zone = url_parts[-3]
    # print(((url).split('/'))[-1])

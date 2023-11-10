from google.cloud import compute_v1

def list_all_subnets(project_id):
    client = compute_v1.SubnetworksClient()
    subnets = client.aggregated_list(project=project_id)
    # print(len(subnets))
    # print(subnets.get('items', {}).items())
    i = 0
    for subnet in subnets:
        print((subnet[1].subnetworks[0].name))
        # print(len(subnet))
        i = i + 1
        print(i)

def sample_list(project_id):
    # Create a client
    client = compute_v1.RoutesClient()
    route = client.get(project=project_id, route="default-route-efb2c6f83a3c1634")
    print(route)

    # Initialize request argument(s)
    # request = compute_v1.ListRoutesRequest(
    #     project=project_id,
    # )

    # # Make the request
    # page_result = client.list(request=request)
    # print(type(page_result))
    # # Handle the response
    # for response in page_result:
    #     # route_attributes = dir(response)
    #     # print(route_attributes)
    #     # break
    #     print(response)
        
if __name__ == "__main__":
    project_id = "mhrt-dev3-389609"
    sample_list(project_id)
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
    # url = "https://www.googleapis.com/compute/v1/projects/mhrt-dev3-389609/zones/us-east1-b/instances/tf-instance-thu2"

    # # Tách chuỗi bằng dấu '/'
    # url_parts = url.split('/')

    # # Lấy tên máy ảo và khu vực
    # machine_name = url_parts[-1]
    # zone = url_parts[-3]
    # print(f"{url.split('/')[-1]} (Zone {url.split('/')[-3]})")

from google.oauth2 import service_account
from googleapiclient import discovery

# Replace with your GCP project ID
project_id = 'mhrt-dev3-389609'

# Load your service account key file
service_account_file = 'gcpkey.json'

# Authenticate with your service account key
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Create a service object for Cloud DNS
dns = discovery.build('dns', 'v1', credentials=credentials)

# List DNS policies
policies = dns.policies().list(project=project_id).execute()
# Print the list of policies
for policy in policies.get('policies', []):
    # print(policy.get('description', ''))
    print(f"Policy ID: {policy['routing_config']}, Name: {policy['name']}, Description: {policy['description']}")

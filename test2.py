from __future__ import annotations

from collections.abc import Iterable

from google.cloud import compute_v1
project = 'mhrt-dev3-389609'

def list_firewall_rules(project_id: str) -> Iterable[compute_v1.Firewall]:
    """
    Return a list of all the firewall rules in specified project. Also prints the
    list of firewall names and their descriptions.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.

    Returns:
        A flat list of all firewall rules defined for given project.
    """
    firewall_client = compute_v1.FirewallsClient()
    firewalls_list = firewall_client.list(project=project_id)

    for firewall in firewalls_list:
        print(f" - {firewall.name}: {firewall.description}")

    return firewalls_list


print(type(list_firewall_rules(project)))
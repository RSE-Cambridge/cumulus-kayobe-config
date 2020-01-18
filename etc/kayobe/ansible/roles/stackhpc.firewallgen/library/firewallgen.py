from ansible.module_utils.basic import AnsibleModule
from firewallgen import ssutils
from firewallgen import haproxy
from firewallgen import iputils
from firewallgen import dockerutils
from firewallgen import utils
from firewallgen import firewallgen
from firewallgen.firewallgen import (TCPDataCollectorIPV4Mapped, UDPDataCollectorIPV4Mapped,
                                     UDPDataCollector, TCPDataCollector, collect_open_sockets)
from operator import itemgetter

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

def process_to_dict(process):
    return vars(process)

def opensocket_to_dict(opensocket):
    result = vars(opensocket)
    result['processes'] = map(process_to_dict, result['processes'])
    return result

def run_module():
    module_args = dict(
        ip_to_interface_map=dict(type='dict', required=True),
        # dest=dict(type='str', required=True)
        ip_version=dict(type='int', required=False, default=4)
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    map_ = module.params['ip_to_interface_map']
    ip_to_interface = firewallgen.InterfaceMap(map_)

    if module.params['ip_version'] == 4:
        tcp = collect_open_sockets(TCPDataCollector(ip_to_interface))
        udp = collect_open_sockets(UDPDataCollector(ip_to_interface))
        if utils.is_ipv4_mapped_ipv6_enabled():
            tcp_mapped = collect_open_sockets(TCPDataCollectorIPV4Mapped(ip_to_interface))
            udp_mapped = collect_open_sockets(UDPDataCollectorIPV4Mapped(ip_to_interface))
            tcp.extend(tcp_mapped)
            udp.extend(udp_mapped)
    else:
        raise NotImplementedError("ipv6 support not currently implemented")

    allsockets= map(opensocket_to_dict, (tcp+udp))

    hinter = haproxy.get_hinter()
    for socket in allsockets:
        for process in socket["processes"]:
            if process["name"] == "haproxy":
                process["haproxy_hint"] = hinter(socket["ip"], socket["port"])

    result['sockets'] = sorted(allsockets, key = itemgetter('proto', 'interface', 'port', 'ip'))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

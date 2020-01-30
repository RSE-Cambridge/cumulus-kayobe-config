stackhpc.firewallgen
=========================

Generates an iptables firewall by inspecting the target host for any open sockets

Requirements
------------

- `kayobe` is required for it's filters and variables
- `jq` is required for firewall rule rewriting

Role Variables
--------------

    # list of rules to accept in the filter chain
    firewallgen_ipv4_input_allow_rules: []

    # where to output the generated firewall rules
    firewallgen_output_path: "{{ kayobe_config_path | dirname ~ '/firewallgen' }}"

    # location where the iptables-restore file is outputed prior to being loaded
    firewallgen_rules_path: /tmp/firewallgen-iptables.rules

    # where, on the target host, to output a backup of the iptables rules
    firewallgen_backup_path: /tmp/firewallgen-iptables.save

    # firewall must be explicitly enabled to be applied
    firewallgen_enable_firewall: False

    # modify the generated rules with `jq` expressions:
    # e.g to remove the rule generated for the process, `rpcbind`, you
    # could use: '. | map(select(.processes[].name != "rpcbind"))'
    firewallgen_ipv4_input_allow_rewrite_rules: []

    # list of network names to perform `net_name | net_vip_address`
    # and `net_name | net_vip_address` lookups against. If the
    # network_name doesn't refer to a variable it will be interpretted
    # as a string literal, e.g:
    firewallgen_networks:
      - "oob_oc_net_name"
      - "provision_oc_net_name"
      - "oob_wl_net_name"
      - "provision_wl_net_name"
      - "internal_net_name"
      - "public_net_name"
      - "inspection_net_name"
      - "cleaning_net_name"
      - "storage_net_name"
      - "storage_mgmt_net_name"
      # networks without an associated name
      - "devops"
      # external networks
      - "oc_provision"
      - "eod_hs_eth"

    # any custom rules not picked up by firewallgen, e.g:
    firewallgen_ipv4_input_allow_custom_rules:
      # docker registry - ss doesn't show docker forwarded ports unless
      # EXPOSE is set: https://stackoverflow.com/questions/36454955/docker-and-netstat-netstat-is-not-showing-ports-exposed-by-docker-containers
    - interface: "{% raw %}{{ oc_provision_interface }}{% endraw %}"
      port: 5000
      proto: tcp
      destination: "{% raw %}{{ 'oc_provision' | net_ip }}{% endraw %}"

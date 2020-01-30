stackhpc.ssm
=========

Deploys Secure Stomp Messenger

Requirements
------------

Requires `docker` and `git` to be configured on the host.

Role Variables
-----------------

Please see `defaults/main.yml`.

Dependencies
------------

None

Example Playbook
--------------------

Using a shared volume with the caso container:

```
- name: Converge
  hosts: all
  vars:
    pip_install_packages:
      - name: docker
    ssm_sender_enabled: true
    ssm_outgoing_volume: caso_ssm_outgoing
  pre_tasks:
    - name: install dependencies
      package:
        name: "{{ item }}"
      with_items:
        - git
  roles:
    - geerlingguy.pip
    - geerlingguy.docker
    - role: stackhpc.ssm
      vars:
        ssm_action: build
    - role: stackhpc.ssm
      vars:
        ssm_action: deploy
```

Where `caso_ssm_outgoing` is bind mounted to `ssm.output_path` in ``caso.conf``.

License
-------

Apache

Author Information
------------------

Will Szumski

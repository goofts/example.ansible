# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    example-executor
    ~~~~~~~~~~~~~~~~

    Implements Ansible Playbook entry by CLI

    Usage:
        python3 example-executor.py

    :author:    goofts <goofts@zl.com>
    :homepage:  https://github.com/goofts
    :license:   LGPL, see LICENSE for more details.
    :copyright: Copyright (c) 2019 Goofts. All rights reserved
"""
import sys

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 5):
    print ("must use python version > 3.5")
    sys.exit(-1)

try:
    from ansible.inventory.manager import InventoryManager
    from ansible.vars.manager import VariableManager
    from ansible.parsing.dataloader import DataLoader
    from ansible.executor.playbook_executor import PlaybookExecutor
    from ansible.executor.task_queue_manager import TaskQueueManager
    from ansible.module_utils.common.collections import ImmutableDict
    from ansible.playbook.play import Play
    from ansible.plugins.callback import CallbackBase
    from ansible.cli import CLI
    from ansible import context
    from optparse import Values
    import ansible.constants as C
    import json
except:
    print ("please run `pip3 install -r requirements` to install packages first")
    sys.exit(-1)

class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_result = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

        if "msg" in result._result:
            msg = result._result["msg"]
            for key, value in msg.items():
                self.result[key] = value

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result
    
    def getResult(self):
        return self.host_result

options = Values({
    "verbosity":0 ,
    "ask_pass": False,
    "private_key_file": None,
    "remote_user": "ansible",
    "connection": "smart",
    "timeout": 10,
    "ssh_common_args": "",
    "sftp_extra_args": "",
    "scp_extra_args": "",
    "ssh_extra_args": "",
    "force_handlers": False,
    "flush_cache": None,
    "become": False,
    "become_method": "sudo",
    "become_user": None,
    "become_ask_pass": False,
    "tags": ["all"],
    "skip_tags": [],
    "check": False,
    "syntax": None,
    "diff": False,
    "inventory": ["./hosts"],
    "listhosts": None,
    "subset": "server_a",
    "extra_vars": ["targetHost=server_b","sourseHost=server_a"],
    "ask_vault_pass": False,
    "vault_password_files": [],
    "vault_ids": [],
    "forks": 5,
    "module_path": None,
    "listtasks": None,
    "listtags": None,
    "step": None,
    "start_at_task": None,
})

context._init_global_context(options)
loader, inventory, variable_manager = CLI._play_prereqs()
CLI.get_host_list(inventory, context.CLIARGS["subset"])

pbex = PlaybookExecutor(
    playbooks=["./playbooks/roles/common/tasks/main.yml"],
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords=dict(conn_pass = "goofts@123",become_pass = "goofts@123")
)

result_callback = ResultCallback()
pbex._tqm._stdout_callback = result_callback
result_id = pbex.run()
result = result_callback.getResult()
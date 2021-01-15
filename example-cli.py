# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    example-cli
    ~~~~~~~~~~~

    Implements Ansible Playbook entry by CLI

    Usage:
        python3 example-cli.py

    :author:    goofts <goofts@zl.com>
    :homepage:  https://github.com/goofts
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2019 Goofts. All rights reserved
"""
import sys

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 5):
    print ("must use python version > 3.5")
    sys.exit(-1)

try:
    from ansible import context
    from ansible import constants as C
    from ansible.cli.playbook import PlaybookCLI
    from ansible.plugins.callback import CallbackBase
    from ansible.cli import CLI
    from ansible.executor.playbook_executor import PlaybookExecutor
    import json
    import re
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

cli = PlaybookCLI([" ", "-i", "./hosts", "--limit", "server_a", "-e", "targetHost=server_b", "-e", "sourseHost=server_a", "./playbooks/roles/common/tasks/main.yml"])

super(PlaybookCLI,cli).run()

loader, inventory, variable_manager = cli._play_prereqs()

CLI.get_host_list(inventory, context.CLIARGS["subset"])

pbex = PlaybookExecutor(
    playbooks=context.CLIARGS["args"],
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords=None
)

result_callback = ResultCallback()
pbex._tqm._stdout_callback = result_callback
result_id = pbex.run()
result = result_callback.getResult()
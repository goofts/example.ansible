# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    example-play
    ~~~~~~~~~~~~

    Implements Ansible Playbook entry by CLI

    Usage:
        python3 example-play.py

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
    from ansible.playbook.play import Play
    from ansible.plugins.callback import CallbackBase
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

loader=DataLoader()
inventory = InventoryManager(
    loader=loader,
    sources=["./hosts"]
)
variable_manager = VariableManager(loader=loader, inventory=inventory)

play_source = dict(
    name = "测试",
    hosts = "server_a",
    gather_facts = "no",
    remote_user = "ansible",
    connection = "ssh",
    tasks = [
        dict(action=dict(module="command", args="ls -la ~"), register="resultInfo"),
        dict(action=dict(module="debug", args=dict(msg='"{{ resultInfo.stdout }}"'))),
    ]
)

play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
result_callback = ResultCallback()

tqm = None
try:
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=dict(conn_pass = "goofts@123",become_pass = "goofts@123"),
        stdout_callback=result_callback,
        run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
        run_tree=False,
    )
    result_id = tqm.run(play)
finally:
    if tqm is not None:
        tqm.cleanup()

results_raw = {}
results_raw["success"] = {}
results_raw["failed"] = {}
results_raw["unreachable"] = {}

for host, result in result_callback.host_ok.items():
    results_raw["success"][host] = json.dumps(result._result)

for host, result in result_callback.host_failed.items():
    results_raw["failed"][host] = result._result["msg"]

for host, result in result_callback.host_unreachable.items():
    results_raw["unreachable"][host] = result._result["msg"]

if "success" in results_raw:
    for key, value in results_raw["success"].items():
        result = json.loads(value)
        print (key)
        print (result["msg"].strip('"'))
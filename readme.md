# ansible

### run ansible with cli
```
python3 example-cli.py
```

### run ansible with executor
```
python3 example-executor.py
```

### run ansible with play
```
python3 example-play.py
```

### run ansible with playbook
```
ansible-playbook --limit server_a -e "targetHost=server_b" -e "sourseHost=server_a" ./playbooks/roles/common/tasks/main.yml
```

### 该 demo 是使用 ansible 的剧本来控制两台主机，并使其自动化测试双向流量带宽的范例
### 该 demo 是为了介绍使用 python 控制 ansible 剧本的3种方法
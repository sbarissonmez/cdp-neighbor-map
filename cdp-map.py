from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir.core.filter import F
import time
import getpass

nr = InitNornir(config_file="/config.yaml")

Set Credentials for Group
# Enter Username for Switch in Group
access_user = input('Enter Access Username: ')
# Enter password for Device in Group in Hosts.yaml
access_password = getpass.getpass(prompt="Access Switch password: ")
nr.inventory.groups['group'].username = access_user  # set Username for Group
# set password for Group
nr.inventory.groups['group'].password = access_password

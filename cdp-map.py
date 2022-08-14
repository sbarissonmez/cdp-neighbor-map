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
# set Username for Group
nr.inventory.groups['group'].username = access_user
# set password for Group
nr.inventory.groups['group'].password = access_password

# Get all Interfaces for given VLAN and enable CDP on them
def cdp_enable(task):
    r = task.run(task=netmiko_send_command,
                 command_string="sh vlan", use_genie=True)
    task.host["facts"] = r.result
    try:
        interfaces = r.result['vlans']['xx']['interfaces']
    except:
        print('no configurable Interfaces in VLAN<XX> available!')
    else:
        print(interfaces)
        for intf in interfaces:
            cdp_enable = task.run(netmiko_send_config, name="Enable CDP on Interface " +
                                  intf, config_commands=["interface " + intf, "cdp enable"])
        time.sleep(60)  # Wait 60 Seconds to detect new CDP Neighbors


def cdp_map(task):
    r = task.run(task=netmiko_send_command,
                 command_string="show cdp neighbor detail", use_genie=True)
    task.host["facts"] = r.result
    outer = task.host["facts"]
    indexer = outer['index']
    for idx in indexer:
        local_intf = indexer[idx]['local_interface']
        remote_port = indexer[idx]['port_id']
        remote_id_domain = indexer[idx]['device_id']
        remote_id = remote_id_domain.split('.local')[0]
        cdp_config = task.run(netmiko_send_config, name="Automating CDP Network Descriptions", config_commands=[
            "interface " + str(local_intf),
            "description " + str(remote_id)]
        )


def cdp_map_po(task):
    r = task.run(task=netmiko_send_command,
                 command_string="show etherchannel sum", use_genie=True)
    task.host["portchannel"] = r.result
    portchannel = task.host["portchannel"]
    interfaces = portchannel['interfaces']
    for poch in interfaces:
        member_intf = interfaces[poch]['port_channel']['port_channel_member_intfs'][0]
        des = task.run(task=netmiko_send_command, command_string="show interface {} description".format(
            member_intf), use_genie=True)
        member_des = des.result['interfaces'][member_intf]['description']
        task.run(netmiko_send_config, name="Automating CDP Network Descriptions Port-Channel", config_commands=[
            "interface " + str(poch),
            "description " + str(member_des)]
        )


results_enable = nr.run(task=cdp_enable)
results_map = nr.run(task=cdp_map)
results_map_po = nr.run(task=cdp_map_po)
write_mem = nr.run(task=netmiko_send_command,
                   command_string="write mem", use_genie=True)

print_result(results_enable)
print_result(results_map)
print_result(results_map_po)
print_result(write_mem)

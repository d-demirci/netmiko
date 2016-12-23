#!/usr/bin/env python
from netmiko import ConnectHandler
import re

ip_addr = '000.000.000.000'


ssh_device = {
    'device_type': 'gaia_os_ssh',
    'ip': ip_addr,
    'username': 'username',
    'password': 'password*',
    'secret': 'expert_password',
    'verbose': True
}


print "SSH"
net_connect = ConnectHandler(**ssh_device)
# print "SSH prompt: {}".format(net_connect.find_prompt())
# print "send_command: "
# print '-' * 50
# print net_connect.send_command("show time")
# print '-' * 50
print "entering expert mode: "
print net_connect.enable()
# print "in expert mode: "
# print '-' * 50
# print "send_command: "
# print net_connect.send_command("cpstat")
# print '-' * 50
# print "entering dbedit mode: "
# print net_connect.dbedit()
# print "in dbedit mode: "
# print '-' * 50
# print "send_command: "
# policies = net_connect.send_command("print fw_policies ##Bestepe-int-Policy")
# # policies_dict = parse(xml_input=policies)
# print policies
# print '-' * 50
# print "exiting dbedit mode: "
# print net_connect.exit_dbedit()
# print '-' * 50
print "send_command: CD $FWDIR"
print net_connect.send_command("cd #FWDIR")
# print "in #FWDIR"
# print "entering queryDB_util mode: "
#print net_connect.querydb_util()
#print "in queryDB_util mode: "
# print '-' * 50
print "send_command: "
# hosts = net_connect.send_command("-t network_objects -s type='host' -pf")
hosts = net_connect.send_command("echo -e \"localhost\n-t network_objects -s type='host' -pf\n-q\" | queryDB_util | egrep 'Object Name|ipaddr:'")
print "write output to file"

host_names_file = open(r"D:\Python_Output\netmiko\host_names.txt", 'w')
ip_addr_file = open(r"D:\Python_Output\netmiko\ip_addr.txt", 'w')
all_file = open(r"D:\Python_Output\netmiko\all.txt", 'w')

hosts = hosts.encode('utf-8')

all_file.write(hosts)

p_host = re.compile('Object Name: (.*)')
p_ips = re.compile('ipaddr: (.*)')

host_names = p_host.findall(hosts)
host_ips = p_ips.findall(hosts)
# target.write(host_names)
for item in host_names:
    host_names_file.write(item)
    host_names_file.write("\n")

for item in host_ips:
    ip_addr_file.write(item)
    ip_addr_file.write("\n")

# target.write(host_ips)
all_file.close()
host_names_file.close()
ip_addr_file.close()
#print hosts
print "exiting queryDB_util mode: "
print net_connect.exit_querydb_util()
# print '-' * 50
print "exiting expert mode: "
print net_connect.exit_enable_mode()
# print '-' * 50
# print '-' * 50
print "close session"
print net_connect.disconnect()
print "session closed"

#todo exit session
#output = net_connect.send_command_expect("show version")
#print
#print '#' * 50
#print output
#print '#' * 50
#print

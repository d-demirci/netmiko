#!/usr/bin/env python
# -*- coding: utf-8 -*-
from netmiko import ConnectHandler
import re
import sys, getopt
import os


"""This file connects to checkpoint management server and
using the expert password queries checkpoint objects using queryDB_util
the used query gets ip and host names on the firewall checks with previous ones and reports back the differences."""

def main(argv):
    ip_addr = ''
    username = ''
    password = ''
    secret = ''

    try:
        opts, args = getopt.getopt(argv, "hi:u:p:s:d", ["ip_addr=", "username=", "password=", "secret="])
    except getopt.GetoptError:
        print 'test_checkpoint_simple.py -i <ip_addr> -u <username> -p <ssh_pass> -s <expert_pass>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'test.py -i <ip_addr> -u <username> -p <ssh_pass> -s <expert_pass>'
            sys.exit()
        elif opt in ("-i", "--ip_addr"):
            ip_addr = arg
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-s", "--secret"):
            secret = arg
        elif opt == '-d':
            global _debug
            _debug = arg

            #    print 'Ip Address is :', ip_addr
            #    print 'Username is :', username
            #    print 'Password is :', password
            #    print 'Secret is :', secret
            #    print '\n'

    ssh_device = {
        'device_type': 'gaia_os_ssh',
        'ip': ip_addr,
        'username': username,
        'password': password,
        'secret': secret,
        'verbose': False
    }

    #    print "SSH"
    net_connect = ConnectHandler(**ssh_device)
    #    print "entering expert mode: "
    net_connect.enable()
    #    print "send_command: CD $FWDIR"
    net_connect.send_command("cd #FWDIR")
    #    print "send_command: "
    hosts = net_connect.send_command(
        "echo -e \"localhost\n-t network_objects -s type='host' -pf\n-q\" | queryDB_util | egrep 'Object Name|ipaddr:'")
    #    print "write output to file"
    net_connect.exit_querydb_util()
    net_connect.exit_querydb_util()
    #    print "exiting expert mode: "
    net_connect.exit_enable_mode()
    #    print "close session"
    net_connect.disconnect()

    pre_host_names_file_name = r"/home/forensic/Documents/netmiko/host_names.txt"
    pre_ip_addr_file_name = r"/home/forensic/Documents/netmiko/ip_addr.txt"
    pre_all_file_name = r"/home/forensic/Documents/netmiko/all.txt"

    pre_host_names_file = open(pre_host_names_file_name, 'r')
    pre_ip_addr_file = open(pre_ip_addr_file_name, 'r')
    pre_all_file = open(pre_all_file_name, 'r')

    cur_host_names_file_name = r"/home/forensic/Documents/netmiko/cur_host_names.txt"
    cur_ip_addr_file_name = r"/home/forensic/Documents/netmiko/cur_ip_addr.txt"
    cur_all_file_name = r"/home/forensic/Documents/netmiko/cur_all.txt"

    cur_host_names_file = open(cur_host_names_file_name, 'w')
    cur_ip_addr_file = open(cur_ip_addr_file_name, 'w')
    cur_all_file = open(cur_all_file_name, 'w')

    hosts = hosts.encode('utf-8')

    cur_all_file.write(hosts)

    p_host = re.compile('Object Name: (.*)')
    p_ips = re.compile('ipaddr: (.*)')

    host_names = p_host.findall(hosts)
    host_ips = p_ips.findall(hosts)
    cur_host_name_count = 0
    for item in host_names:
        cur_host_name_count += 1
        cur_host_names_file.write(item)
        cur_host_names_file.write("\n")

    cur_ip_addr_count = 0
    cur_ip_list = []
    for item in host_ips:
        if item is not "" and [0 <= int(x) < 256 for x in
                               re.split('\.', re.match(r'^\d+\.\d+\.\d+\.\d+$', item).group(0))].count(True) == 4:
            cur_ip_addr_file.write(item)
            cur_ip_addr_file.write("\n")
            cur_ip_addr_count += 1
            cur_ip_list.append(item + "\n")

    pre_host_names_count = 0
    for line in pre_host_names_file:
        if line is not "\n":
            pre_host_names_count += 1

    pre_ip_addr_count = 0
    pre_ip_list = []
    for line in pre_ip_addr_file:
        if line is not "\n":
            pre_ip_addr_count += 1
            pre_ip_list.append(line)

    change_in_host_count = cur_host_name_count - pre_host_names_count
    change_in_ip_addr_count = cur_ip_addr_count - pre_ip_addr_count

    # renaming files :
    os.remove(pre_all_file_name)
    os.remove(pre_ip_addr_file_name)
    os.remove(pre_host_names_file_name)

    os.rename(cur_host_names_file_name, pre_host_names_file_name)
    os.rename(cur_ip_addr_file_name, pre_ip_addr_file_name)
    os.rename(cur_all_file_name, pre_all_file_name)

    effected_ips = ""
    if change_in_ip_addr_count > 0:
        for line in cur_ip_list:
            exists = False
            for newline in pre_ip_list:
                if line == newline:
                    exists = True
                    break
            if not exists:
                effected_ips += str(line).replace("\n", "") + ","
        print "Tanimli IP/Istemci:{}/{}-Eklenen IP:{}/Istemci:{}/Etkilenen IPler:{}".format(cur_ip_addr_count,
                                                                                            cur_host_name_count,
                                                                                            change_in_ip_addr_count,
                                                                                            change_in_host_count,
                                                                                            effected_ips)
    elif change_in_ip_addr_count < 0:
        for line in pre_ip_list:
            exists = False
            for newline in cur_ip_list:
                if line == newline:
                    exists = True
                    break
            if not exists:
                effected_ips += str(line).replace("\n", "") + ","
        print "Tanimli IP/Istemci:{}/{}-Silinen IP:{}/Istemci:{}/Etkilenen IPler:{}".format(cur_ip_addr_count,
                                                                                            cur_host_name_count,
                                                                                            change_in_ip_addr_count,
                                                                                            change_in_host_count,
                                                                                            effected_ips)

    else:
        print "IP ve Istemci Sayisinda Degisiklik Yok"

if __name__ == "__main__":
    main(sys.argv[1:])


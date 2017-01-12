#!/usr/bin/env python

from __future__ import print_function
from netmiko import ConnectHandler
from os import path


def main():
    try :
        ip_addr = raw_input("Enter remote host ip to test: ")
    except NameError:
        ip_addr = input("Enter remote host ip to test: ")

    try:
        username = raw_input("Enter username: ")
    except NameError:
        username = input("Enter username: ")

    try:
        password = raw_input("Enter password: ")
    except NameError:
        password = input("Enter password: ")

    ssh_device = {
        'device_type': 'gaia_os_ssh',
        'ip': ip_addr,
        'username': username,
        'password': password,
        'verbose': True
    }

    #    print "SSH"
    net_connect = ConnectHandler(**ssh_device)

    allowed_hosts = net_connect.send_command(command_string="show allowed-client all")

    print(allowed_hosts)

    net_connect.send_command(command_string="add allowed-client network ipv4-address 10.3.39.0 mask-length 24")

    after = net_connect.send_command(command_string="show allowed-client all")

    print(after)

    print()
    net_connect.disconnect()

if __name__ == "__main__":
    main()

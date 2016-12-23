import re
import socket
import time

from netmiko.cisco_base_connection import CiscoSSHConnection
from netmiko.ssh_exception import NetMikoTimeoutException


class GaiaOsSSH(CiscoSSHConnection):
    def disable_paging(self, *args, **kwargs):
        """Gaia doesn't have paging by default."""
        return ""

    def set_base_prompt(self, pri_prompt_terminator='>',
                        alt_prompt_terminator='#', delay_factor=1):
        """Determine base prompt."""
        return super(CiscoSSHConnection, self).set_base_prompt(
            pri_prompt_terminator=pri_prompt_terminator,
            alt_prompt_terminator=alt_prompt_terminator,
            delay_factor=delay_factor)

    def send_config_set(self, config_commands=None, exit_config_mode=True, **kwargs):
        """Can't exit from root (if root)"""
        if self.username == "root":
            exit_config_mode = False
        return super(CiscoSSHConnection, self).send_config_set(config_commands=config_commands,
                                                               exit_config_mode=exit_config_mode,
                                                               **kwargs)

    def check_config_mode(self, check_string='#'):
        """Verify root"""
        return self.check_enable_mode(check_string=check_string)

    def config_mode(self, config_command='sudo su'):
        """Attempt to become root."""
        return self.enable(cmd=config_command)

    def exit_config_mode(self, exit_config='exit'):
        return self.exit_enable_mode(exit_command=exit_config)

    def check_enable_mode(self, check_string='#'):
        """Verify root"""
        return super(CiscoSSHConnection, self).check_enable_mode(check_string=check_string)

    def exit_enable_mode(self, exit_command='exit'):
        """Exit enable mode."""
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        if self.check_enable_mode():
            self.write_channel(self.normalize_cmd(exit_command))
            time.sleep(.3 * delay_factor)
            self.set_base_prompt()
            if self.check_enable_mode():
                raise ValueError("Failed to exit expert mode.")
        return output

    def enable(self, cmd='expert', pattern='password:', re_flags=re.IGNORECASE):
        """Attempt to become expert."""
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        time.sleep(.3 * delay_factor)
        if not self.check_enable_mode():
            self.write_channel(self.normalize_cmd(cmd))
            time.sleep(1 * delay_factor)
            pattern = re.escape(pattern)
            try:
                time.sleep(.3 * delay_factor)
                output += self.read_channel()
                time.sleep(.3 * delay_factor)
                if re.search(pattern, output, flags=re_flags):
                    self.write_channel(self.normalize_cmd(self.secret))
                time.sleep(.3 * delay_factor)
                self.set_base_prompt(pri_prompt_terminator='.', alt_prompt_terminator='#')
            except socket.timeout:
                raise NetMikoTimeoutException("Timed-out reading channel, data not available.")
            if not self.check_enable_mode():
                raise ValueError("Failed to enter expert mode.")
        return output

    def dbedit(self, cmd='dbedit', pattern="localhost')", re_flags=re.IGNORECASE):
        """Attempt to become expert."""
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        """If current mode is Expert mode then let enter dbedit """
        if self.check_enable_mode(check_string='#'):
            self.write_channel(self.normalize_cmd(cmd))
            time.sleep(.3 * delay_factor)
            pattern = re.escape(pattern)
            try:
                output += self.read_channel()
                if re.search(pattern, output, flags=re_flags):
                    self.write_channel(self.normalize_cmd('\n\r'))
                    output = self.read_channel()
                self.set_base_prompt()
            except socket.timeout:
                raise NetMikoTimeoutException("Timed-out reading channel, data not available.")
            if not self.check_enable_mode(check_string='>'):
                raise ValueError("Failed to enter dbedit mode.")
        return output

    def exit_dbedit(self, exit_command='-q'):
        """Exit enable mode."""
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        if self.check_enable_mode(check_string='>'):
            self.write_channel(self.normalize_cmd(exit_command))
            time.sleep(.3 * delay_factor)
            self.set_base_prompt()
            if not self.check_enable_mode():
                raise ValueError("Failed to exit dbedit mode.")
        return output

    def querydb_util(self, cmd='queryDB_util', pattern='name:', re_flags=re.IGNORECASE):
        """Attempt to user queryDB_util."""
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        """If current mode is Expert mode then let enter dbedit """
        if self.check_enable_mode(check_string='#'):
            self.write_channel(self.normalize_cmd(cmd))
            time.sleep(.3 * delay_factor)
            pattern = re.escape(pattern)
            try:
                output += self.read_channel()
                if re.search(pattern, output, flags=re_flags):
                    self.write_channel(self.normalize_cmd('\n\r'))
                    output = self.read_channel()
                self.set_base_prompt()
            except socket.timeout:
                raise NetMikoTimeoutException("Timed-out reading channel, data not available.")
            if not self.check_enable_mode(check_string='>'):
                raise ValueError("Failed to enter queryDB_util mode.")
        return output

    def exit_querydb_util(self, exit_command='-q'):
        """Exit queryDB_util mode."""
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        if self.check_enable_mode(check_string='>'):
            self.write_channel(self.normalize_cmd(exit_command))
            time.sleep(.3 * delay_factor)
            self.set_base_prompt()
            if not self.check_enable_mode():
                raise ValueError("Failed to exit queryDB_util mode.")
        return output

    def disconnect(self):
        delay_factor = self.select_delay_factor(delay_factor=0)
        output = ""
        exit_command ="exit"
        if self.check_enable_mode(check_string='>'):
            self.write_channel(self.normalize_cmd(exit_command))
            time.sleep(.3 * delay_factor)
            # self.set_base_prompt()
            # if not self.check_enable_mode(check_string="."):
            #     raise ValueError("Failed to close session.")
        return output
from netmiko import ConnectHandler
from server.orm import RouterUser


class RouterConnection:
    def __init__(self, host_ip: str, username: str, password: str):
        self.connector_dict_default = {
            'device_type': 'cisco_ios',
            'host': host_ip,
            'username': username,
            'password': password,
        }
        self.conn: ConnectHandler = None
        self.transaction_queue: [] = []

    def __repr__(self):
        return self.connector_dict_default.__repr__()

    def start_transaction(self):
        self.conn: ConnectHandler = ConnectHandler(**self.connector_dict_default)
        self.transaction_queue = []

    def add_instructions_to_transaction(self, instructions: []):
        self.transaction_queue += instructions

    def execute_transaction(self):
        value: str = ""
        for instruction in self.transaction_queue:
            ret = self.conn.send_command_timming(instruction)
            value += ret
        self.conn = None
        self.transaction_queue = []
        return value

    def shutdown_all_protocols(self):
        instruction_set_shutdown_all_protocols = ["clear ip route *",
                                                  "configure terminal",
                                                  "no router ospf 1",
                                                  "no router rip",
                                                  "exit"]
        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_shutdown_all_protocols)
        self.execute_transaction()

    def configure_rip_protocol(self):
        self.shutdown_all_protocols()
        instruction_set_enable_rip = \
            ["TODO", "instruction"]
        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_enable_rip)
        self.execute_transaction()

    def configure_ospf_protocol(self):
        self.shutdown_all_protocols()
        self.conn: ConnectHandler = ConnectHandler(**self.connector_dict_default)
        instructions = ["configure terminal",
                        # TODO
                        "exit"]
        for instruction in instructions:
            self.conn.send_command(instruction)
        self.conn = None

    def configure_interface_create_queue(self, interface: str):
        self.start_transaction()
        str1 = f"configure terminal"
        str2 = f"interface {interface}"
        instructions = [str1, str2]
        self.add_instructions_to_transaction(instructions)

    def add_admin_router_user(self, user: RouterUser):
        pass

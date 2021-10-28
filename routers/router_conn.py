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
            print(instruction)
            ret = self.conn.send_command_timing(instruction)
            value += ret
            print(ret)
        self.conn = None
        self.transaction_queue = []
        return value

    def add_static_ip_route(self, network: (str, str, str)):
        (ip, mask, next_hop) = network
        value = f"ip route {ip} {mask} {next_hop}"
        instruction_set_shutdown_all_protocols = ["configure terminal",
                                                  value,
                                                  "exit"]
        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_shutdown_all_protocols)
        self.execute_transaction()

    def shutdown_static_ip_route(self, network: (str, str)):
        (ip, mask) = network
        value = f"no ip route {ip} {mask}"
        instruction_set_shutdown_all_protocols = ["configure terminal",
                                                  value,
                                                  "exit"]
        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_shutdown_all_protocols)
        self.execute_transaction()

    def no_ospf(self, protocol_name:str):
        self.start_transaction()
        self.add_instructions_to_transaction(["configure terminal", f"no router ospf {protocol_name}"])
        self.execute_transaction()

    def no_rip(self):
        self.start_transaction()
        self.add_instructions_to_transaction(["configure terminal", "no router rip"])
        self.execute_transaction()

    def no_eigrp(self, protocol_name:str):
        self.start_transaction()
        self.add_instructions_to_transaction(["configure terminal", f"no router eigrp {protocol_name}"])
        self.execute_transaction()

    def configure_rip_protocol(self, network_array: []):
        instruction_set_enable_rip = ["configure terminal", "router rip", "version 2"]
        result = []
        for network in network_array:
            result += [f"network {network}"]
        instruction_set_enable_rip += result
        instruction_set_enable_rip += ["no auto-summary", "exit", "exit"]

        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_enable_rip)
        value = self.execute_transaction()
        return value

    def configure_ospf_protocol(self, network_array: [], name: str):
        instruction_set_enable_ospf = ["configure terminal", f"router ospf {name}"]
        result = []
        for network in network_array:
            result += [f"network {network.ip_network}  {network.wildcard} area {network.num_area} "]
        instruction_set_enable_ospf += result
        instruction_set_enable_ospf += [ "exit", "exit"]
        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_enable_ospf)
        value = self.execute_transaction()
        return value

    def configure_eigrp_protocol(self, network_array: [], name: str):
        instruction_set_enable_eigrp = ["configure terminal", f"router ospf {name}"]
        result = []
        for network in network_array:
            result += [f"network {network}"]
        instruction_set_enable_eigrp += result
        instruction_set_enable_eigrp += [ "exit", "exit"]
        self.start_transaction()
        self.add_instructions_to_transaction(instruction_set_enable_eigrp)
        value = self.execute_transaction()
        return value

    def configure_interface_create_queue(self, interface: str):
        self.start_transaction()
        str1 = f"configure terminal"
        str2 = f"interface {interface}"
        instructions = [str1, str2]
        self.add_instructions_to_transaction(instructions)

    def add_router_user(self, user: RouterUser, password: str):
        str1 = f"configure terminal"
        str2 = f"username {user.user_name} privilege {user.user_type} secret {password}"
        self.start_transaction()
        self.add_instructions_to_transaction([str1, str2])
        self.execute_transaction()

    def drop_router_user(self, user: RouterUser):
        str1 = f"configure terminal"
        str2 = f"no username {user.user_name}"
        self.start_transaction()
        self.add_instructions_to_transaction([str1, str2])
        self.execute_transaction()

    def update_router_user(self, user: RouterUser, password: str):
        self.drop_router_user(user)
        self.add_router_user(user, password)


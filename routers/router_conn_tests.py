from routers.router_conn import RouterConnection


class RouterTests:
    @staticmethod
    def test_ping_pong():
        conn = RouterConnection("10.0.2.254", "root", "root")
        conn.start_transaction()
        conn.add_instructions_to_transaction(["show ip route", "show ip route"])
        value = conn.execute_transaction()
        print(value)
        assert (1 + 1, 2)

    @staticmethod
    def test_delete_routing_protocols():
        conn = RouterConnection("10.0.2.254", "root", "root")
        value = conn.shutdown_all_protocols()
        print(value)

        conn.start_transaction()
        conn.add_instructions_to_transaction(["show ip route"])
        value = conn.execute_transaction()

        print(value)
        assert (1 + 1, 2)


    @staticmethod
    def test_enable_rip():
        conn: RouterConnection = RouterConnection("10.0.2.254", "root", "root")
        value = conn.configure_rip_protocol(["10.0.2.0", "10.0.3.0"])

        conn: RouterConnection = RouterConnection("10.0.3.2", "root", "root")
        value = conn.configure_rip_protocol(["10.0.1.0", "10.0.3.0"])


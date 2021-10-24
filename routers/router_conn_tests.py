from router_conn import RouterConnection


class RouterTests():
    @staticmethod
    def test_ping_pong():
        conn = RouterConnection("10.0.2.254", "root", "root")
        conn.start_transaction()
        conn.add_instructions_to_transaction(["show ip route"])
        value = conn.execute_transaction()
        print(value)
        assert (1 + 1, 2)

from routers.router_conn_tests import RouterTests


if __name__ == '__main__':
    RouterTests.test_ping_pong()
    RouterTests.test_delete_routing_protocols()
    RouterTests.test_enable_rip()



from client.client_main import Client
import sys

client_id = 1 if len(sys.argv) == 1 else int(sys.argv[1])
Client(client_id).run()

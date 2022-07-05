import json
from .processes import *

def get_enodes(network):
  output = run_and_output(f'docker network inspect {network}')
  containers = json.loads(output)[0]['Containers']
  enodes = {}

  for container in containers:
    ip = containers[container]['IPv4Address']
    ip = ip.split('/')[0] # Remove CIDR part.

    enode = run_and_output(f'docker exec -it {container} geth --exec "console.log(admin.nodeInfo.enode)" attach')
    enode = enode.split('\n')[0]
    enode = enode.strip()
    enode = enode.replace('127.0.0.1', ip)

    enodes[container] = enode

  return enodes

def connect_all(enodes):
  for container in enodes:
    for peer in enodes:
      run_and_output(f'docker exec -it {container} geth --exec "admin.addPeer(\'{enodes[peer]}\')" attach')

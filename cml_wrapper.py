import argparse
import os
from virl2_client import ClientLibrary 
from datetime import datetime
from pyaml_env import parse_config
import json
from dotenv import load_dotenv

load_dotenv()

#################### FIREWALL ##########################
f2= open("./asa_config.txt", "r")
os.environ["ASA_CONFIG"] = f2.read()
f2.close()
#################### Router #############################
with open(r'./router_config.txt', 'r') as file:  
    data = file.read()  
    data = data.replace('GigabitEthernet0/0/0', 'GigabitEthernet1')
    data = data.replace('GigabitEthernet0/0/1', 'GigabitEthernet2')
    data = data.replace('GigabitEthernet0/0/2', 'GigabitEthernet3')
    data = data.replace('GigabitEthernet0/0/3', 'GigabitEthernet4')

with open(r'./router_config.txt', 'w') as file:
    file.write(data)

f3= open("./router_config.txt", "r")
os.environ["ROUTER_CONFIG"] = f3.read()
f3.close()
##################### SWITCH ###########################
with open(r'./switch_config.txt', 'r') as file:  
    data = file.read()  
    data = data.replace('interface GigabitEthernet1/0/23', 'interface GigabitEthernet0/0')
    data = data.replace('interface GigabitEthernet1/0/24', 'interface GigabitEthernet0/1')
    data = data.replace('interface GigabitEthernet2/0/23', 'interface GigabitEthernet0/2')
    data = data.replace('interface GigabitEthernet2/0/24', 'interface GigabitEthernet0/3')
    data = data.replace('interface GigabitEthernet1/0/1', 'interface GigabitEthernet1/0')
    data = data.replace('interface GigabitEthernet1/0/2', 'interface GigabitEthernet1/1')
    data = data.replace('interface GigabitEthernet2/0/1', 'interface GigabitEthernet1/2')
    data = data.replace('interface GigabitEthernet2/0/2', 'interface GigabitEthernet1/3')
    data = data.replace('interface GigabitEthernet1/0/9', 'interface GigabitEthernet2/0')
    data = data.replace('interface GigabitEthernet1/0/10', 'interface GigabitEthernet2/1')
    data = data.replace('interface GigabitEthernet3/0/9', 'interface GigabitEthernet2/2')
    data = data.replace('interface GigabitEthernet3/0/10', 'interface GigabitEthernet2/3')

with open(r'./switch_config.txt', 'w') as file:
    file.write(data)

f3= open("./switch_config.txt", "r")
os.environ["ROUTER_CONFIG"] = f3.read()
f3.close()

##################################################################

def import_lab(client, path):
    lab_name = "ci-test-" + datetime.now().strftime("%Y%m%d"+"-%H%M%S")
    print('Importing test topology...')
    lab = client.import_lab_from_path(path, title=lab_name)
    print('Lab ' + lab_name + ' successfully imported. Lab ID is ' + lab.id)
    return lab

parser = argparse.ArgumentParser(description='CI test CML wrapper')    
parser.add_argument('--url', type=str, help='CML host URL (default from env)')
parser.add_argument('--user', type=str, help='CML username (default from env)')
parser.add_argument('--passwd', type=str, help='CML password (default from env)')
parser.add_argument('--topology', type=str, help='CML topology pass (default is ./cml_ci_topology.yaml)')
parser.add_argument('--action', type=str, help='create or destroy (default create)')
args = parser.parse_args()

f1= open("./topology_file.yaml", "w")
f1.write(json.dumps(parse_config('./cml_ci_topology.yaml')))
f1.close()


if args.url == None:
    #args.url = os.environ['VIRL2_URL']
    args.url = 'https://88.244.172.99:17111'
if args.user == None:
    args.user = os.environ['VIRL2_USER']
if args.passwd == None:
    args.passwd = os.environ['VIRL2_PASS']
if args.action == None:
    args.action = 'create'
if args.topology == None:
    args.topology = './topology_file.yaml'

if args.url == None or args.user == None or args.passwd == None:
    print (parser.print_help())
    exit(1)

client_library = ClientLibrary(args.url, args.user, args.passwd, ssl_verify=False)
print('Successfully authenticated with CML controller')

if args.action == 'create':
    lab = import_lab(client_library, args.topology)
    
    f = open(".lab_id", "w")
    f.write(lab.id)
    f.close()
    
    print('Starting ' + lab.title + '...')
    lab.start(wait=True)
    
    print('Done!')
    
if args.action == 'destroy':
    f = open(".lab_id", "r")
    lab_id = f.read()
    f.close()
    
    print('Lab ID is ' + lab_id)
    lab = client_library.join_existing_lab(lab_id)
    
    print('Stoping lab' + lab_id)
    lab.stop()
    
    print('Wiping lab' + lab_id + ' out')
    lab.wipe()
    
    print('Removing lab' + lab_id)
    client_library.remove_lab(lab_id)
    
    print('Done!')

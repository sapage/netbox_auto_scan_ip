import ipcalc
import networkscan
from netbox import NetBox
import requests
import datetime
import json
import socket

requests.packages.urllib3.disable_warnings()


API_TOKEN = "d3a51fe6e4ab6419c731ab0de11335c3682bcd06"
HEADERS = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
NB_URL = "https://10.53.109.145"
netbox = NetBox(host="10.53.109.145", port=443, use_ssl=True, auth_token="d3a51fe6e4ab6419c731ab0de11335c3682bcd06")

if __name__ == '__main__':

    # Define the network to scan
    #my_network = input("Subnet: ")    

    network = ["10.53.109.53/32"]
    for my_network in network:
            
        # Create the object
        my_scan = networkscan.Networkscan(my_network)
        
        # Run the scan of hosts using pings
        my_scan.run()

        # Here we define exists ip address in our network and write it to list    
        found_ip_in_network = []
        for address1 in my_scan.list_of_hosts_found:
            found_ip_in_network.append(str(address1))
        
        # Get all ip from prefix
        for ipaddress in ipcalc.Network(my_network):
            # Doing get request to netbox
            request_url = f"{NB_URL}/api/ipam/ip-addresses/?q={ipaddress}/"
            ipaddress1 = requests.get(request_url, headers = HEADERS, verify=False)
            netboxip = ipaddress1.json()
           # print(pretty_obj)
            if netboxip['count'] == 0:
                # Check if in network exists and not exist in netbox
                if ipaddress in found_ip_in_network:
                    # Adding in IP netbox
                    netbox.ipam.create_ip_address(str(ipaddress))
                else:
                    pass        
            else:
                #If not exists in netbox and network
                if ipaddress in found_ip_in_network:
                    addr = socket.gethostbyaddr(str(ipaddress))
                    pretty_obj = json.dumps(netboxip, indent=4)
                    ipam_ip_dict = json.loads(pretty_obj)
                    ipam_ip_url=(ipam_ip_dict['results'][0]['url'])
                    jsonUpdate_temp = '{"vrf": 1, "tenant": 1, "dns_name": "replace", "status": "active"}'
                    jsonUpdate = jsonUpdate_temp.replace('replace', addr[0],1)
                    response = requests.patch(ipam_ip_url, data=(jsonUpdate), headers=HEADERS, verify=False)
                else:
                    netbox.ipam.update_ip(str(ipaddress),status="deprecated")
#

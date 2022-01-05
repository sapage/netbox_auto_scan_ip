import ipcalc
import networkscan
from netbox import NetBox
import requests
import datetime
import json
import dns.resolver

def dns_lookup(host):
  try:
    ans = dns.resolver.resolve_address(host)
    return ans
  except:
    return ""

requests.packages.urllib3.disable_warnings()

API_TOKEN = "xx"
HEADERS = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
NB_URL = "https://10.53.109.145"
netbox = NetBox(host="10.53.109.145", port=443, use_ssl=True, auth_token="xx")

if __name__ == '__main__':

    # Define the network to scan
    #my_network = input("Subnet: ")    

    network = ["10.53.4.0/24", "10.1.0.0/24", "10.53.102.0/24", "10.53.103.0/24", "10.53.110.0/24", "10.53.112.0/24",
     "10.1.15.0/24", "10.1.22.0/24", "10.1.27.0/24", "10.1.29.0/24", "10.1.0.0/24", "10.1.4.0/24", "10.1.5.0/24",
     "10.1.55.0/24", "10.51.2.0", "10.1.14.0/24", "10.1.21.0/24", "10.2.0.0/24", "10.53.2.0/24", "10.51.253.0/24",
     "10.2.55.0/24", "10.51.200.0/24", "10.51.201.0/24", "10.51.206.0/24", "10.53.105.0/24", "10.53.98.0/24",
     "10.53.100.0/24", "10.53.109.0/24", "10.53.115.0/24", "10.53.117.0/24", "10.53.119.0/24", "10.53.124.0/24", 
     "10.53.174.0/24", "10.53.128.0/24", "10.53.101.0/24", "10.53.16.0/24" , "10.53.122.0/24", "10.53.126.0/24",
     "10.53.176.0/24", "10.153.101.0/24", "10.153.102.0/24", "10.153.103.0/24", "10.153.104.0/24", "10.153.105.0/24",
     "10.153.107.0/24", "10.153.108.0/24", "10.153.109.0/24", "10.153.119.0/24", "10.153.120.0/24", "10.153.96.0/24", 
     "10.153.97.0/24", "10.153.98.0/24", "10.153.99.0/24", "10.153.126.0/24", "10.153.127.0/24", "10.153.128.0/24", 
     "10.153.129.0/24", "10.153.100.0/24", "10.53.1.0/24", "10.53.24.0/24", "10.58.1.0/24", "10.53.241.0/24", 
     "10.53.26.0/24", "10.51.24.0/24", "10.51.0.0/24", "10.53.8.0/24", "10.1.0.0/24", "10.53.104.0/24", "10.53.113.0/24", 
     "10.53.114.0/24", "10.1.15.0/24", "10.1.22.0/24", "10.1.27.0/24", "10.1.29.0/24", "10.1.30.0/24", "10.1.34.0/24", 
     "10.1.35.0/24", "10.1.55.0/24", "10.51.24.0/24", "10.1.14.0/24", "10.1.21.0/24", "10.2.0.0/24", "10.53.251.0/24", 
     "10.2.55.0/24", "10.51.202.0/24", "10.51.203.0/24", "10.53.106.0/24", "10.53.107.0/24", "10.53.108.0/24", 
     "10.53.118.0/24", "10.53.120.0/24", "10.53.121.0/24", "10.53.97.0/24", "10.53.125.0/24", "10.53.129.0/24", 
     "10.53.123.0/24", "10.53.127.0/24",  "10.153.119.0/24", "10.153.112.0/24", "10.153.232.0/24", "10.153.233.0/24", 
     "10.53.2.0/24", "10.53.25.0/24", "10.58.2.0/24", "10.53.175.0/24", "10.53.240.0/24", "10.53.242.0/24", 
     "10.53.243.0/24", "10.53.27.0/24"] 
    
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
            netbox_test = (str(netboxip))
            if "'url'" in netbox_test:
                pretty_obj = json.dumps(netboxip, indent=4)
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
                        addr = dns_lookup(str(ipaddress))
                        for answer in addr:
                            answer.to_text()
                            print(answer)
                            pretty_obj = json.dumps(netboxip, indent=4)
                            ipam_ip_dict = json.loads(pretty_obj)
                            ipam_ip_url=(ipam_ip_dict['results'][0]['url'])
                            jsonUpdate_temp = '{"vrf": 1, "tenant": 1, "dns_name": "replace", "status": "active"}'
                            jsonUpdate = jsonUpdate_temp.replace('replace', str(answer))
                            response = requests.patch(ipam_ip_url, data=(jsonUpdate), headers=HEADERS, verify=False)
                    else:
                        netbox.ipam.update_ip(str(ipaddress),status="deprecated")
            elif ipaddress in found_ip_in_network:
                print(str(ipaddress))
                netbox.ipam.create_ip_address(str(ipaddress))
                #jsonUpdate_temp = '{"vrf": 1, "tenant": 1, "dns_name": "replace", "status": "active"}'
                #jsonUpdate = jsonUpdate_temp.replace('replace', str(answer))
                #jsonUpdate = '{"vrf": 1, "tenant": 1, "dns_name": "New IP", "status": "active", "address": "ipadd"}'
                #jsonUpdate = jsonUpdate_temp.replace('ipadd', str(ipaddress))
                #request_url_post = f"{NB_URL}/api/ipam/ip-addresses/"
                #response = requests.post(request_url_post, data=(jsonUpdate), headers=HEADERS, verify=False)
            else:
                print('NO IP Address')

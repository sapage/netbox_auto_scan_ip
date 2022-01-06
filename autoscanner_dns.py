import ipcalc
import networkscan
from netbox import NetBox
import requests
import json
import dns.resolver

def dns_lookup(host):
  try:
    ans = dns.resolver.resolve_address(host)
    return ans
  except:
    return ""

requests.packages.urllib3.disable_warnings()

API_TOKEN = "d3a51fe6e4ab6419c731ab0de11335c3682bcd06"
HEADERS = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
NB_URL = "https://10.53.109.145"
netbox = NetBox(host="10.53.109.145", port=443, use_ssl=True, auth_token="d3a51fe6e4ab6419c731ab0de11335c3682bcd06")

if __name__ == '__main__':

    # Define the network to scan
    #Branch ranges
    network = [ "10.52.0.0/24", "10.52.1.0/24", "10.52.2.0/24", "10.52.3.0/24", "10.52.4.0/24", "10.52.5.0/24", 
    "10.52.6.0/24", "10.52.7.0/24", "10.52.8.0/24", "10.52.9.0/24", "10.52.10.0/24", "10.52.11.0/24", "10.52.12.0/24",
    "10.52.13.0/24", "10.52.14.0/24", "10.52.15.0/24", "10.52.16.0/22", "10.52.18.0/24", "10.52.19.0/24", "10.52.20.0/24", 
    "10.52.21.0/24", "10.52.22.0/24", "10.52.23.0/24", "10.52.28.0/22", "10.52.32.0/24", "10.52.64.0/24", "10.52.76.0/22", 
    "10.54.12.0/24", "10.54.13.0/24", "10.54.14.0/24", "10.54.16.0/22", "10.54.17.0/24", "10.54.18.0/24", "10.54.28.0/22",
    "10.54.29.0/24", "10.54.30.0/24", "10.54.36.0/24", "10.54.36.0/24", "10.54.37.0/24", "10.54.38.0/24", "10.54.48.0/24", 
    "10.54.49.0/24", "10.54.50.0/24", "10.54.60.0/24", "10.54.61.0/24", "10.54.62.0/24", "10.54.64.0/24", "10.54.65.0/24", 
    "10.54.66.0/24", "10.54.68.0/24", "10.54.69.0/24", "10.54.70.0/24", "10.54.72.0/22", "10.54.88.0/24", "10.54.89.0/24", 
    "10.54.90.0/24", "10.54.92.0/24", "10.54.93.0/24", "10.54.94.0/24", "10.54.104.0/28", "10.54.105.0/24", "10.54.106.0/24", 
    "10.54.112.0/24", "10.54.113.0/24", "10.54.114.0/24", "10.54.120.0/24", "10.54.254.0/24"] 
    
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

            #If There is a Netbox IP update DNS if it exists. 
            if "'url'" in netbox_test:
                pretty_obj = json.dumps(netboxip, indent=4)
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

            #If pingable but not in Netbox create Entry
            elif ipaddress in found_ip_in_network:
                print(str(ipaddress))
                netbox.ipam.create_ip_address(str(ipaddress), vrf=1, tenant=1)
                
            #If not pingable mark ad deprecated
            #else:
            #            netbox.ipam.update_ip(str(ipaddress),status="deprecated", vrf=1, tenant=1)
            #Do nothing
            else:
                pass

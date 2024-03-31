import requests

def get_ip_port(website, location):
    url = f"http://192.168.38.10:8080?website={website}&location={location}"
    response = requests.get(url)
    data = response.json()
    return data[website][location]

def make_second_request(ip_address, port_number):
    url = f"http://{ip_address}:{port_number}"
    response = requests.get(url)
    return response.text

website = input("Enter website: ")
location = input("Enter your country: ")

ip_address, port_number = get_ip_port(website, location)

second_request_response = make_second_request(ip_address, port_number)

print('\n'+str(second_request_response)+'\n')
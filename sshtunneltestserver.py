import paramiko
import getpass
from sshtunnel import SSHTunnelForwarder
REMOTE_SERVER_IP = 'sunfire.comp.nus.edu.sg'
PRIVATE_SERVER_IP = '137.132.86.228'

username = input("Enter ssh username: ")
password =  getpass.getpass("Enter ssh password: ")

with SSHTunnelForwarder(
    REMOTE_SERVER_IP,
    ssh_username=username,
    ssh_password=password,
    remote_bind_address=(PRIVATE_SERVER_IP, 22),
    local_bind_address=('0.0.0.0', 10022)
) as tunnel:
    client = paramiko.SSHClient()
    # client.load_system_host_keys(r'C:\Users\youca\.ssh\known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('127.0.0.1', port=10022, username='xilinx', password='xilinx')
    print(client.exec_command('mkdir SUPFMFMOEUFEF'))
    # do some operations with client session
    client.close()

print('FINISH!')
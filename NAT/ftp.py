import netmiko
import os

device = {
    'device_type': 'linux',
    'host': '135.171.48.237',
    'username': 'root',
    'password': 'Alcateldc',
}



def file_send_linux(device):
    net_connect = netmiko.ConnectHandler(**device)

    try:
        net_connect.send_command("mkdir clab-test/configs")
    except:
        print("directory already exist")

    configs = os.listdir("C:\\Users\\emese\\Desktop\\Projects\\NTA\\dev\\Configs")

    for config in configs:
        source = f"C:\\Users\\emese\\Desktop\\Projects\\NTA\\dev\\Configs\\{config}"
        transfer = netmiko.file_transfer(
            ssh_conn= net_connect,
            source_file = source,
            dest_file = config,
            disable_md5 = True,
            direction= "put",
            verify_file= False,
            overwrite_file = True,
            file_system= "/root/clab-test/configs"
        )

        print(transfer)

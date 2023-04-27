import os
import pandas as pd


files = os.listdir()
excel = 'nta_dom102_204.xlsx'

InfraLinks = pd.read_excel(excel, sheet_name="InfraLinks")
Devices = pd.read_excel(excel, sheet_name="Devices")
 

InfraLinks_df = pd.DataFrame(InfraLinks, columns=["local_name", "interface_ports", "farend_name", "farend_interface_ports"])
Device_df = pd.DataFrame(Devices, columns=["system_name", "model"])
Cards_df = pd.DataFrame()

name = input("lab ismi ver: ")


if f"{name}.clab.yaml" in files:
    os.remove(f"{name}.clab.yaml")

f = open(f"{name}.clab.yaml", "a+")


def nodes():

    f.write(f"name: {name}" + "\n"*2 +  "topology:\n" + "  nodes:\n")
    for i in Device_df.iterrows():
        system_name = i[1][0]
        type = str(i[1][1]).strip()
        if type.startswith("7750"):
            type = "sr-1"
        if type.startswith("ixr-r6"):
            type = "ixr-r6"
        elif type.startswith("ixr"):
            type = "ixr-ec"
            
        image = "vrnetlab/vr-sros:22.5.R2"  #Input olarak alacağız
        f.write(f"    {system_name}:\n      kind: vr-sros\n      image: {image}\n      type: {type}\n      license: license22.txt\n")
        
        
def links():
    temp = []
    mapping = dict()

    f.write("  links:\n")
    for i in InfraLinks_df.iterrows():
        local_name = i[1][0]
        interface_ports = i[1][1]
        farend_name = i[1][2]
        farend_interface_ports = i[1][3]
        if local_name and interface_ports:

            if local_name not in mapping.keys():
                mapping[local_name] = dict()
            if interface_ports not in mapping[local_name]:
                mapping[local_name][interface_ports] = f"eth{len(mapping[local_name])+1}"

                           

            if farend_name not in mapping.keys():
                mapping[farend_name] = dict()
            if farend_interface_ports not in mapping[farend_name]:
                mapping[farend_name][farend_interface_ports] = f"eth{len(mapping[farend_name])+1}"
            

        
        if (local_name + ":" + interface_ports) in temp:
            continue
        else:
            temp.append(local_name + ":" + interface_ports)
            if (farend_name + ":" + farend_interface_ports) in temp:
                continue
            else:
                f.write(f"    - endpoints: [\"{local_name}:{mapping[local_name][interface_ports]}\", \"{farend_name}:{mapping[farend_name][farend_interface_ports]}\"]" + "\n")
                temp.append(farend_name + ":" + farend_interface_ports)
     
                
     





nodes()
links()

f.close()




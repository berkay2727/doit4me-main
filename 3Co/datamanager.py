import sqlite3, os , re
from subprocess import Popen
from sys import executable
####################  RULES  #####################
# 1- Make First Character of Global Variable CAPITAL
# 2- Leave at least 3 empty lines before and after a function, if it is not related with top or below functions
# 3- Use CAPITAL LETTERS for FUNCTION DEFINITION and start with "###"
# 4- While creating/naming new OUTPUT REGEX FUNCTIONS
#       * use original command
#       * use "_" instead of removing the spaces 
# 5- Use "#" and start with capital letter while leaving a comment or explanation
##################################################


### GLOBAL DEFINITIONS 
global Session_state_list

Session_state_list =["UpDown_Time"]
Db_connection = sqlite3.connect("outputdb.sqlite")  # Database Creation 
Cur = Db_connection.cursor()


### FUNCTION DB --- TABLE CREATION for A COMMAND
def create_table(table_name:str): 
    Cur.execute(f"""CREATE TABLE IF NOT EXISTS  {table_name} (ID INTEGER NOT NULL PRIMARY KEY UNIQUE, output_folder_id INTEGER NOT NULL, output_file_id INTEGER NOT NULL)""")
    Db_connection.commit



### FUNCTION DB --- AUTO DICTIONARY CREATION from PARAMETER LIST and COLUMN LIST
def create_dictionary_for_table_creation(parameter_map:dict,column_list:set):
    column_and_parameter=dict() 
    for column in column_list:
        for parameter in parameter_map:
            if column in parameter_map[parameter]:
                column_and_parameter[column] = parameter
    return column_and_parameter



### FUNCTION DB --- ADD COLUMN to THE TABLE
def add_column_to_table(table_name:str, column_parameter:dict): #ADD COLUMN
    Cur.execute(f"""pragma table_info({table_name});""")
    existing_column=Cur.fetchall()
    column_set=set()
    for i in existing_column:
        column_set.add(str(i[1]))
    for column in column_parameter:
        parameter = str(column_parameter[column]).upper()
        column=(str(column).title()).replace(" ", "_")
        if column in column_set:
            continue
        Cur.execute(f"""ALTER TABLE {table_name} ADD {column} {parameter}""")
    del column_set
    Db_connection.commit



### FUNCTION DB --- INSERT DATA to COLUMNS in THE TABLE
def insert_data_to_table(table_name:str,pool:dict):
    
    for item_info in pool.values():
        keys, values = str("output_folder_id, output_file_id, "), str(f"{Output_folder_id},{Output_file_id},")
        for key,value in item_info.items():
            if key in Session_state_list:
                value = time_convert_to_seconds(value)
            key, value = str(key), str(value)
            keys += key + ", "
            values+= "'"+value + "',"
        Cur.execute(f"""INSERT INTO {table_name} ({keys[:-2]}) VALUES({values[:-1]})""")




### FUNCTION REGEXs --- PARTIAL FILE SLICING 
def small_regex(regex_definition, parsed_output):
    global small_output
    if re.search(regex_definition, parsed_output, re.MULTILINE) is not None:
        matches = re.finditer(regex_definition, parsed_output, re.MULTILINE)
        for match in matches:
            small_output = match.group()
    else:
        small_output = "" 
      
    return small_output 

def big_regex(specif_command_pattern, a_to_a_pattern, dict_a:dict) -> dict:
    output_pool = {}
    no = 0
    matches = re.finditer(specif_command_pattern, Output, re.MULTILINE)
    for match in matches:
        first_match = match.group()
        a_to_a = re.finditer(a_to_a_pattern, first_match, re.MULTILINE)
        for match_1 in a_to_a:
            no += 1
            output_pool[no]={}
            each_a_to_a = match_1.group()
            for key in dict_a.keys():
                output_pool[no][key] = small_regex(dict_a[key],each_a_to_a)     
    return output_pool



#FUNCTION EXTRA - TIME CONVERTER
def time_convert_to_seconds(value:str):
    value = value.strip()
    if value[-1] == "m":
        d_hm = value.split("d")
        day = int(d_hm[0])
        h_m = d_hm[1].split("h")
        hour = int(h_m[0])
        minute = int(h_m[1].split("m")[0])
        result = (24*3600*day)+(3600*hour)+(60*minute)
    elif value [-1] == "s":
        h_ms = value.split("h")
        hour = int(h_ms[0])
        m_s = h_ms[1].split("m")
        minute = int(m_s[0])
        second = int(m_s[1].split("s")[0])
        result = (3600*hour)+(60*minute)+minute
    else:
        result = value
    
    return result

####################################################################################################
####################################################################################################
####################                NOKIA OUTPUT REGEX FUNCTIONS                ####################
####################################################################################################
####################################################################################################

### FUNCTION DATA - SHOW ROUTER INTERFACE DETAIL

def show_router_interface_detail():
    table_name="show_router_interface_detail"
    create_table(table_name)
    parameter_map={"TEXT"    : ["If_Name", "If_Admin_State","If_Oper_State","Down_Reason_Code","Down_Reason_v4","Down_Reason_v6",
                                "Protocols","Last_Oper_Chg","IP_AddrMask","IP_Oper_MTU","Tx_V4_Discard_Pk","Tx_V6_Discard_Pk"],
                  }                 
    neededlist   =             ["If_Name", "If_Admin_State","If_Oper_State","Down_Reason_Code","Down_Reason_v4","Down_Reason_v6",
                                "Protocols","IP_AddrMask","Last_Oper_Chg","IP_Oper_MTU","Tx_V4_Discard_Pk","Tx_V6_Discard_Pk"]
    add_column_to_table(table_name,create_dictionary_for_table_creation(parameter_map, neededlist))
    
    regex_showrouterinterfacedetail = r"(^(A|B):.*[\#\s+|\>\s+|\$\s+]){0,1}show router interface detail([\S\s]*?)(?=(A|B):.*(?=[\#|\>|\$]))"
    regex_ifnametoifname = r"((If Name)([\S\s]*?)((?=(If Name))|(=====)))"
    dict_showrouterinterfacedetail =    {"If_Name"           : r"((?<=If\sName\s{10}:\s).*)", 
                                         "If_Admin_State"    : r"((?<=Admin State\s{6}:\s)(Up|Down))", 
                                         "If_Oper_State"     : r"((?<=Oper \(v4/v6\)\s{6}:\s)((Up/Down)|(Up/Up)|(Down/Down)))",
                                         "Down_Reason_Code"  : r"((?<=Down Reason Code\s{1}:\s)(.*)(?!(\s\S)))",
                                         "Down_Reason_v4"    : r"((?<=Down Reason V4\s{3}:\s)(.*)(?!(\s\S)))",
                                         "Down_Reason_v6"    : r"((?<=Down Reason V6\s{3}:\s)(.*)(?!(\s\S)))",
                                         "Protocols"         : r"((?<=Protocols\s{8}:\s)((?!Not Assigned).*))",
                                         "Last_Oper_Chg"     : r"((?<=Last Oper Chg\s{4}:\s)(.*)(?=(.*Global)))",
                                         "IP_Oper_MTU"       : r"((?<=IP Oper MTU\s{6}:\s)(\d*))",
                                         "IP_AddrMask"       : r"((?<=IP Addr/mask\s{5}:\s)(.*)(?=(.*Address)))",
                                         "Tx_V4_Discard_Pk"  : r"((?<=Tx V4 Discard Pk\*:\s)(\d*)(?=(.*Tx)))",
                                         "Tx_V6_Discard_Pk"  : r"((?<=Tx V6 Discard Pk\*:\s)(\d*)(?=(.*Tx)))"
                                    }
    insert_data_to_table(table_name,big_regex(regex_showrouterinterfacedetail,regex_ifnametoifname, dict_showrouterinterfacedetail))
    
    Db_connection.commit


### FUNCTION DATA - SHOW ROUTER BGP SUMMARY ALL
def show_router_bgp_summary_all():
    table_name="show_router_bgp_summary_all"
    create_table(table_name)
    parameter_map={"TEXT"    : ["Service_Id","Neighbor","Family_Ipv4","Family_Ipv6", "Family_Vpnipv4", "Family_Vpnipv6",
                                "Family_Mvpnipv4","Family_Routetarget","Family_Mvpnipv6","Family_Evpn","Family_Label_Ipv4", "Family_Label_Ipv6",
                                ],\
                   "INTEGER" : ["UpDown_Time", 
                                "Family_Ipv4_Rec", "Family_Ipv4_Act", "Family_Ipv4_Sent",
                                "Family_Ipv6_Rec", "Family_Ipv6_Act", "Family_Ipv6_Sent",
                                "Family_Vpnipv4_Rec", "Family_Vpnipv4_Act", "Family_Vpnipv4_Sent",
                                "Family_Vpnipv6_Rec","Family_Vpnipv6_Act","Family_Vpnipv6_Sent",
                                "Family_Mvpnipv4_Rec","Family_Mvpnipv4_Act","Family_Mvpnipv4_Sent",
                                "Family_Routetarget_Rec","Family_Routetarget_Act","Family_Routetarget_Sent",
                                "Family_Mvpnipv6_Rec","Family_Mvpnipv6_Act","Family_Mvpnipv6_Sent",
                                "Family_Evpn_Rec","Family_Evpn_Act","Family_Evpn_Sent",
                                "Family_Label_Ipv4_Rec", "Family_Label_Ipv4_Act", "Family_Label_Ipv4_Sent",
                                "Family_Label_Ipv6_Rec", "Family_Label_Ipv6_Act", "Family_Label_Ipv6_Sent"]\
                  }                 
    neededlist =               ["Service_Id","Neighbor","UpDown_Time",
                                "Family_Ipv4_Rec", "Family_Ipv4_Act", "Family_Ipv4_Sent",
                                "Family_Ipv6_Rec", "Family_Ipv6_Act", "Family_Ipv6_Sent",
                                "Family_Vpnipv4_Rec", "Family_Vpnipv4_Act", "Family_Vpnipv4_Sent", 
                                "Family_Vpnipv6_Rec","Family_Vpnipv6_Act","Family_Vpnipv6_Sent",
                                "Family_Mvpnipv4_Rec","Family_Mvpnipv4_Act","Family_Mvpnipv4_Sent",
                                "Family_Routetarget_Rec","Family_Routetarget_Act","Family_Routetarget_Sent",
                                "Family_Mvpnipv6_Rec","Family_Mvpnipv6_Act","Family_Mvpnipv6_Sent",
                                "Family_Evpn_Rec","Family_Evpn_Act","Family_Evpn_Sent",
                                "Family_Label_Ipv4_Rec", "Family_Label_Ipv4_Act", "Family_Label_Ipv4_Sent",
                                "Family_Label_Ipv6_Rec", "Family_Label_Ipv6_Act", "Family_Label_Ipv6_Sent"
                                ]
    add_column_to_table(table_name,create_dictionary_for_table_creation(parameter_map, neededlist))
    
    regex_showrouterbgpsummaryall = r"(^(A|B):.*[\#\s+|\>\s+|\$\s+]){0,1}show router bgp summary all([\S\s]*?)(?=(A|B):.*(?=[\#|\>|\$]))"
    regex_iptoip = r"((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))([\S\s]*?)(?=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?=(------)))"
    dict_showrouterbgpsummaryall =      {"Neighbor"               : r"^(\d*\.\d*\.\d*\.\d*)$",
                                         "Service_Id"             : r"^(Def\. Instance|Svc:\s\d*)(?=\s*\d*)",
                                         "UpDown_Time"       : r"((\d{2,3}[a-z]\d{2}[a-z]\d{2}[a-z]))",
                                         "Family_Ipv4_Rec"        : r"(?<=\s)\b\d*\b(?=/.*\b(IPv4)\b)",
                                         "Family_Ipv4_Act"        : r"(?<=/)\b\d*\b(?=/.*\b(IPv4)\b)",
                                         "Family_Ipv4_Sent"       : r"(?<=/)\d*(?=\s\(IPv4\))",
                                         "Family_Ipv6_Rec"        : r"(?<=\s)\b\d*\b(?=/.*\b(IPv6)\b)",
                                         "Family_Ipv6_Act"        : r"(?<=/)\b\d*\b(?=/.*\b(IPv6)\b)",
                                         "Family_Ipv6_Sent"       : r"(?<=/)\d*(?=\s\(IPv6\))",
                                         "Family_Label_Ipv4_Rec"  : r"(?<=\s)\b\d*\b(?=/.*\b(label-ipv4)\b)",
                                         "Family_Label_Ipv4_Act"  : r"(?<=/)\b\d*\b(?=/.*\b(label-ipv4)\b)",
                                         "Family_Label_Ipv4_Sent" : r"(?<=/)\d*(?=\s\(label-ipv4\))",
                                         "Family_Label_Ipv6_Rec"  : r"(?<=\s)\b\d*\b(?=/.*\b(label-ipv6)\b)",
                                         "Family_Label_Ipv6_Act"  : r"(?<=/)\b\d*\b(?=/.*\b(label-ipv6)\b)",
                                         "Family_Label_Ipv6_Sent" : r"(?<=/)\d*(?=\s\(label-ipv6\))",
                                         "Family_Vpnipv4_Rec"     : r"(?<=\s)\b\d*\b(?=/.*\b(VpnIPv4)\b)",
                                         "Family_Vpnipv4_Act"     : r"(?<=/)\b\d*\b(?=/.*\b(VpnIPv4)\b)",
                                         "Family_Vpnipv4_Sent"    : r"(?<=/)\d*(?=\s\(VpnIPv4\))",
                                         "Family_Vpnipv6_Rec"     : r"(?<=\s)\b\d*\b(?=/.*\b(VpnIPv6)\b)",
                                         "Family_Vpnipv6_Act"     : r"(?<=/)\b\d*\b(?=/.*\b(VpnIPv6)\b)",
                                         "Family_Vpnipv6_Sent"    : r"(?<=/)\d*(?=\s\(VpnIPv6\))",
                                         "Family_Mvpnipv4_Rec"    : r"(?<=\s)\b\d*\b(?=/.*\b(MvpnIPv4)\b)",
                                         "Family_Mvpnipv4_Act"    : r"(?<=/)\b\d*\b(?=/.*\b(MvpnIPv4)\b)",
                                         "Family_Mvpnipv4_Sent"   : r"(?<=/)\d*(?=\s\(MvpnIPv4\))",
                                         "Family_Routetarget_Rec" : r"(?<=\s)\b\d*\b(?=/.*\b(RouteTarget)\b)",
                                         "Family_Routetarget_Act" : r"(?<=/)\b\d*\b(?=/.*\b(RouteTarget)\b)",
                                         "Family_Routetarget_Sent": r"(?<=/)\d*(?=\s\(RouteTarget\))",
                                         "Family_Mvpnipv6_Rec"    : r"(?<=\s)\b\d*\b(?=/.*\b(MvpnIPv6)\b)",
                                         "Family_Mvpnipv6_Act"    : r"(?<=/)\b\d*\b(?=/.*\b(MvpnIPv6)\b)",
                                         "Family_Mvpnipv6_Sent"   : r"(?<=/)\d*(?=\s\(MvpnIPv6\))",
                                         "Family_Evpn_Rec"        : r"(?<=\s)\b\d*\b(?=/.*\b(Evpn)\b)",
                                         "Family_Evpn_Act"        : r"(?<=/)\b\d*\b(?=/.*\b(Evpn)\b)",
                                         "Family_Evpn_Sent"       : r"(?<=/)\d*(?=\s\(Evpn\))"
                                        }

    insert_data_to_table(table_name,big_regex(regex_showrouterbgpsummaryall,regex_iptoip, dict_showrouterbgpsummaryall))
    
    Db_connection.commit







####################################################################################################
####################################################################################################
####################                       MAIN FUNCTIONS                       ####################
####################################################################################################
####################################################################################################

### FUNCTION READ&EXTRACT --- READ DATA TXT FILE and EXTRACT to DATABASE
def read_and_extract(file_path:str):
    global Output 
    read_output_of_file = open(file_path, "r") 
    Output = read_output_of_file.read()
       
    #Read the command file 
    runned_command_file=file_path.split("_Nokia_")
    runned_command_file=runned_command_file[1]
    read_runned_command_file = open(f"{Cur_dir}\\command_db\\Nokia_{runned_command_file}","r")
    runned_command_file_lines = read_runned_command_file.readlines()
    
    for line_of_runned in runned_command_file_lines:
        command_converted = line_of_runned.strip().replace(" ","_")
        if command_converted in Available_function_list:
            function_run=globals()[command_converted]
            function_run()
    
    read_output_of_file.close()
        
    

### FUNCTION MAIN !!!
def main():
    global Output_folder_id, Output_file_id, Cur_dir,Available_function_list
    ### TABLE CREATION for OUTPUT FOLDER and OUTPUT FILE
    Cur_dir=os.getcwd() #Current Directory
    output_dir=f"{Cur_dir}\\output\\" #Directory of Output Folders
    Cur.execute(f"""CREATE TABLE IF NOT EXISTS Output_Folders (ID INTEGER NOT NULL PRIMARY KEY UNIQUE, Output_Foldername TEXT NOT NULL UNIQUE)""")
    Cur.execute(f"""CREATE TABLE IF NOT EXISTS Output_Filenames (ID INTEGER NOT NULL PRIMARY KEY UNIQUE, Output_File TEXT NOT NULL UNIQUE)""")
    #Find available function in datamanager.py and add it to list
    Available_function_list = list()
    read_datamanager_file = open(f"{Cur_dir}\\datamanager.py","r")
    datamanager_file_lines=read_datamanager_file.readlines()
    for line_of_dm in datamanager_file_lines:
        if line_of_dm.startswith("def "):
            Available_function_list.append(line_of_dm.strip().removeprefix("def ").removesuffix("():"))
    read_datamanager_file.close()
    
    for output_folder in os.scandir(output_dir):
        Cur.execute("SELECT COUNT (*) FROM Output_Folders WHERE Output_Foldername = ?", (output_folder.name,))
        output_folder_count = Cur.fetchone()[0]

        if output_folder_count == 0:    
            Cur.execute("INSERT OR IGNORE INTO Output_Folders (Output_Foldername) VALUES(?)", (output_folder.name,))
            Cur.execute("SELECT ID FROM Output_Folders WHERE Output_Foldername = ?", (output_folder.name,))
            Output_folder_id = Cur.fetchone()[0]
            for file in os.scandir(output_folder.path):
                Cur.execute("INSERT OR IGNORE INTO Output_Filenames (Output_File) VALUES(?)", (file.name,))
                Cur.execute("SELECT ID FROM Output_Filenames WHERE Output_File = ?", (file.name,))
                Output_file_id = Cur.fetchone()[0]
                read_and_extract(file.path)
                
main()
print("Outputs were logged in Database")
Popen([executable, "compare.py"])
Db_connection.commit()
Db_connection.close()










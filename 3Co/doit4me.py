### LIBRARIES
import os, netmiko,configparser
from getpass import getpass
from datetime import datetime
from time import sleep, ctime
from pytz import timezone, common_timezones
from pandas import to_datetime
from subprocess import Popen
from sys import executable
####################  RULES  #####################
# 1- Make First Character of Global Variable CAPITAL
# 2- Leave at least 3 empty lines before and after a function, if it is not related with top or below functions
# 3- Use CAPITAL LETTERS for FUNCTION DEFINITION and start with "###"
# 4- Use "#" and start with capital letter while leaving a comment or explanation
##################################################
Percentage_list = ["show router bgp summary all", "show router interface detail"]



### FUNCTION CLI - CLI WRONG INPUT PROTECTION
def selectionfromCLI(section_name:str,section_list:list):
    list_no = 0
    section_name = section_name.title() 
    section_list.sort()
    print("\n"+"-"*5,section_name.upper(),"SELECTION","-"*5)
    for item in section_list:
        print(list_no+1,f"\t", item.title())
        list_no += 1
    while True:
        # FOR THE SELECTION IN COMMAND SECTION
        if section_name.upper() == "COMMAND FILE":
            selected_number= input(f"Choose the command files from the list. Use comma(,) for multiple file selection:\n(Ex: 1,3,2)\n")
        else: # FOR THE SELECTION IN OTHER SECTIONS
            selected_number = input(f"Select the {section_name} Number:")
        if selected_number == "q":
            quit("Quited!")
        try:
            wrong_selection = str()
            # FOR THE SELECTION IN COMMAND SECTION
            if section_name.upper() == "COMMAND FILE": 
                selected_number_list = selected_number.split(",")
                renumbered_selected_number_list =[]
                for selected_id in selected_number_list:
                    wrong_selection = selected_id
                    renumbered_selected_number=int(selected_id)-1 # Convert to array numbers -- starting from 0 instead of 1
                    if 0 <= renumbered_selected_number < len(section_list):
                        renumbered_selected_number_list.append(renumbered_selected_number)
                        continue
                    else:
                        raise ValueError()
                if 0 < len(renumbered_selected_number_list):
                    return renumbered_selected_number_list
            selected_number = int(selected_number)-1
            if 0 <= selected_number <len(section_list):
                return selected_number
            else:
                    print(f"{wrong_selection} is not valid number! Please enter the",section_name,"Number or 'q' for quiting")
        except:
                print(f"{wrong_selection} is not valid entry! Please enter the",section_name,"Number or 'q' for quiting")



### FUNCTION TIME - FORMAT of CURRENT TIME(CT)
def current_time_format(arg):
    now_timezone = to_datetime(datetime.now(timezone((Selected_timezone)))) #Current Time  according to Selected Timezone
    now_for_cli=now_timezone.strftime("%Y %B %d %A %H:%M:%S UTC%z")
    now_for_folder=now_timezone.strftime("%Y%m%d_%H%M%S_UTC%z")
    if arg == "cli":
        
        return now_for_cli
    
    if arg == "folder":
    
        return now_for_folder
    
    if arg == "now":
    
        return now_timezone



### FUNCTION VENDOR - VENDOR SELECTION
def vendor_selection() -> list:
    global Vendor_name, Vendor_type
    
    vendor_list = [("Nokia","nokia_sros"), ("Cisco","cisco_ios")] #("Vendorname,devicetype")
    vendor_list.sort()
    vendornamelist=[]
    for vendorname, vendortype in vendor_list:
        vendornamelist.append(vendorname)
    Vendor_name, Vendor_type = vendor_list[selectionfromCLI("VENDOR",vendornamelist)]



### FUNCTION SESSION - SESSION TYPE SELECTION AND SESSION CONTROLLER FOR SELECTED SESSION TYPE
def session_type_selection():
    global Connection_type_list, Selected_session_type
    
    Connection_type_list = ["Connect and Disconnect","Connect and Stay Connected"] #Connection Type
    Selected_session_type = int(selectionfromCLI("Session Type",Connection_type_list))

def session_controller(self):
    if Connection_type_list[Selected_session_type] == Connection_type_list[0]: # for IPBB NETWORK
        Session.disconnect()
        print (f"\n%s\nConnection has been Closed."%(current_time_format("cli")))
        sleep(Interval_second)
    if Connection_type_list[Selected_session_type] == Connection_type_list[1]: # for MSP NETWORK
        for i in range(0,Interval_second): #Will send whitespace to keep to connection UP
            if i%300 == 0:
                Session.send_command(f"")
            sleep(1)
    pass



### FUNCTION TIMEZONE - TIMEZONE SELECTION
def timezone_selection():
    global Selected_timezone
    
    continents = ["Africa", "America","Antarctica","Arctic","Asia","Australia","Canada", "Europe", "Indian", "Pacific", "UTC"]
    selected_continent = selectionfromCLI("TIME ZONE - CONTINENT",continents)
    cities =[]
    for city in common_timezones:
        if city.startswith(continents[selected_continent]):
            cities.append(city)
    Selected_timezone = cities[selectionfromCLI("TIME ZONE - CITY", cities)]
    print(f"Selected Time Zone is : {Selected_timezone}")



### FUNCTION COMMAND FILE - COMMAND FILE SELECTION
def command_file_selection():
    global Command_file_diroctory, Current_directory, Verified_selected_command_file_dict, Percentage_flag
    Percentage_flag = False
    
    
    Current_directory = os.getcwd()
    Command_file_diroctory = f"{Current_directory}\\command_db\\" #Command Files' Directory
    vendor_command_filename_list = [] #Command Filename List according to Selected Vendor
    for command_file in os.listdir(Command_file_diroctory):
        if command_file.startswith(Vendor_name):
            if os.path.isdir(Command_file_diroctory+f"{command_file}") == True:
                continue
            vendor_command_filename_list.append(command_file)

    while True:
        selected_command_file_number = selectionfromCLI("COMMAND FILE",vendor_command_filename_list) 
        selected_command_file_dict = dict()  #COMMAND FILE NAME:COMMAND FILE PATH
        for number in selected_command_file_number:
            selected_command_file_dict[vendor_command_filename_list[number]] = Command_file_diroctory+vendor_command_filename_list[number]
        Verified_selected_command_file_dict = dict()
        for command_filename in selected_command_file_dict:
            result_of_percentage_per_file, percentage_flag_for_command, file_stay = False, False, True
            notshowcommand=False
            open_selected_command_file = open(selected_command_file_dict[command_filename])
            if os.stat(selected_command_file_dict[command_filename]).st_size < 1:
                if len(open_selected_command_file.read().strip())<1:
                    print('\nFILE IS EMPTY, REMOVED FROM THE LIST:', command_filename)
                continue
            for command in open_selected_command_file:
                if command.strip() in Percentage_list:
                    percentage_flag_for_command = True
                    result_of_percentage_per_file = percentage_flag_for_command and file_stay
                if not command.startswith("show"):
                    print("\n"+"!"*3,command.rstrip())
                    notshowcommand=True 
            if notshowcommand ==True:
                print("\nThis file contains commands other than show command:", command_filename)
                approval=input("Do you want to proceed with this file?(y/n):")
                if approval.lower() == "y":
                    Verified_selected_command_file_dict[command_filename] = selected_command_file_dict[command_filename]
                    open_selected_command_file.close()
                    file_stay = True
                    result_of_percentage_per_file = percentage_flag_for_command and file_stay
                    Percentage_flag = Percentage_flag or result_of_percentage_per_file
                    continue
                elif approval.lower() == "n":
                    print("The command file was removed from the selection list:",command_filename)
                    open_selected_command_file.close()
                    file_stay = False
                    result_of_percentage_per_file = percentage_flag_for_command and file_stay
                    Percentage_flag = Percentage_flag or result_of_percentage_per_file
                    continue
                else:
                    print("The command file was skipped because of wrong input:",command_filename)
                    open_selected_command_file.close()
                    file_stay = False
                    result_of_percentage_per_file = percentage_flag_for_command and file_stay
                    Percentage_flag = Percentage_flag or result_of_percentage_per_file
                    continue
            Percentage_flag = Percentage_flag or result_of_percentage_per_file
            Verified_selected_command_file_dict[command_filename] = selected_command_file_dict[command_filename]
            open_selected_command_file.close()
            print(Percentage_flag)
        if len(Verified_selected_command_file_dict)>0:
            break
        else:
            print("\n\nCommand list is empty. Please select command from the list or quit(q)")
  
 
 
### FUNCTION COMPARE PERCENTAGE
def compare_percentage():
    config = configparser.RawConfigParser()
    config.add_section('Compare')
    percentage = input("Please enter the percentage value to compare outputs:\n[Default value is 5]\n")
    if percentage =="":
        percentage = 5
    config.set('Compare', 'percentage', f"{percentage}")
    with open('init.cfg', 'w+') as configfile:
        config.write(configfile)
        
        
        
        
### FUNCTION OUTPUT- OUTPUT FOLDER MANAGER
def output_manager():
    global Output_folder_directory
    Output_folder_directory = f"{Current_directory}" + "\\output"
    Output_db_sql = f"{Current_directory}" + "\\outputdb.sqlite"
    if os.path.exists(Output_folder_directory) == True:
        last_modified_time_directory = ctime(os.path.getmtime(Output_folder_directory))
        last_modified_time_directory = last_modified_time_directory.replace(":","")
        os.rename(f"{Output_folder_directory}",f"{Output_folder_directory}_{last_modified_time_directory}")
    os.mkdir(Output_folder_directory)
    if os.path.exists(Output_db_sql) == True:
        last_modified_time_db = ctime(os.path.getmtime(Output_db_sql))
        last_modified_time_db = last_modified_time_db.replace(":","")
        os.rename(f"{Output_db_sql}",f"{Output_db_sql}_{last_modified_time_db}")
    print(f"New output folder created.({Output_folder_directory})")
    

### FUNCTION OUTPUT- OUTPUT SUBFOLDER CREATION  
def subfolder_create():
    output_subfolder_directory=f"{Output_folder_directory}\%s"%(current_time_format("folder")) #Subfolder name
    if os.path.exists(output_subfolder_directory) == False:
        os.mkdir(output_subfolder_directory)
        
    return output_subfolder_directory



### FUNCTION SCHEDULER - INTERVAL and END TIME
def scheduler():
    global End_time, Interval_second
    
    while True:
        try:
            End_time = input(f"\nPlease enter the end date&time for the collection:\n(year-month-day-hour-minute <>2022-01-31-23-59)\nCurrent Time at %s: %s\n"%(Selected_timezone,current_time_format("cli")))
            if End_time == "q":
                quit("Quited!")
            datetime.strptime(End_time, "%Y-%m-%d-%H-%M")
            End_time=to_datetime(End_time, format ="%Y-%m-%d-%H-%M")
            End_time=End_time.tz_localize(Selected_timezone)
            if End_time < current_time_format("now"):
                print("End date and time can't be in the past.")
                continue
            break
        except:
            print(f"\n!"*3,f"\nIncorrect data format, should be YYYY-MM-DD-HH-MM",f"\n!"*3)

    while True:
        try:
            interval_min = int(input("Please enter the collection interval(minute):"))
            Interval_second = 60*interval_min
            if 0 < interval_min:
                break
            else:
                print("Please enter the number greater than zero(0).")
        except:
            print(f"\n!"*3,"\nPlease enter the number greater than zero(0).",f"\n!"*3)



####################################################################################################
####################################################################################################
####################                       MAIN FUNCTIONS                       ####################
####################################################################################################
####################################################################################################
def main():
    global Session
    
    vendor_selection()
    command_file_selection()
    if Percentage_flag == True:
        compare_percentage()
    timezone_selection()
    scheduler()
    session_type_selection()
    
    #GET SSH CREDENTIALS
    sessionConfirm = False   
    while (sessionConfirm == False):
        target_hostname = input("\nNodename or IP:")
        target_hostname = target_hostname.strip() #Remove spaces at the beginning and at the end of the string
        husername = input("Username:")
        husername = husername.strip()
        hpassword =  getpass("Password:")
        hpassword = hpassword.strip()
        try:
            print("-"*60,f"""\n{current_time_format("cli")}\nConnection has being Initiated...""")
            Session = netmiko.ConnectHandler(device_type = Vendor_type, ip = target_hostname, username = husername, password = hpassword)
            sessionConfirm = True
                   
        except netmiko.NetMikoAuthenticationException:
            print("Authentication error. Credentials are wrong!\nControl+Z to interrupt.")
        except netmiko.NetmikoTimeoutException:
            print("Connection timeout!\nControl+Z to interrupt.")
    print(f"\n%s\nConnection has been Established" %(current_time_format("cli")))
    
    output_manager()
    
    while End_time > current_time_format("now"):
        if Session.is_alive() == False:
            print("-"*60,f"\n%s\nConnection has being Initiated..." %(current_time_format("cli")))
            Session = netmiko.ConnectHandler(device_type = Vendor_type, ip = target_hostname, username = husername, password = hpassword)
            print(f"\n%s\nConnection has been Established" %(current_time_format("cli")))
        out_dir=subfolder_create()
        for file in Verified_selected_command_file_dict:
            print(f"\nCommmands in {file} are sending to the node...")
            filepath = open(f"{Command_file_diroctory}"+file)
            for cmd in filepath:
                last_read, read_timeout = 0.1, 10
                if cmd.startswith("monitor"):
                    monitor_repeat,monitor_interval = 10,11 # repeat_count, repeat_interval(secs)
                    list_of_words = cmd.split()
                    if "repeat" in cmd:
                        monitor_repeat = int(list_of_words[list_of_words.index("repeat") + 1])
                    if "interval" in cmd:
                        monitor_interval = int(list_of_words[list_of_words.index("interval") + 1])
                    read_timeout = (monitor_interval*monitor_repeat)+2
                    last_read = read_timeout-1
                output=Session.send_command_timing(cmd, last_read=last_read, read_timeout=read_timeout, strip_command=False, strip_prompt=False)
    
                if Vendor_name == "Cisco" and cmd.startswith("monitor"):
                    sleep(read_timeout-5)
                    output=Session.send_command("q",read_timeout=read_timeout,strip_command=False,strip_prompt=False)
    
    
                output_filename = f"\{target_hostname}_{file}"
                with open(out_dir+output_filename,"a+",encoding="utf-8") as ofile:
                    ofile.write("\n"+output)
                ofile.close()
            print (f"\n%s\nOutputs were logged. Output filepath:{out_dir+output_filename}" %(current_time_format("cli")))
        
        Popen([executable, os.getcwd()+"\datamanager.py"])
        
        if (End_time-current_time_format("now")).total_seconds()<Interval_second:
            Session.disconnect()
            print(f"\n%s\nSelected end time is closer than the next collection time.\nConnection has been closed." %(current_time_format("cli")))
            break
        session_controller(Interval_second)
        
    print("\n"+current_time_format("cli")+f"\nProcess has been COMPLETED.")
    
main()
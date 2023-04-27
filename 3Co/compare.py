import sqlite3, pandas,os,configparser
from time import ctime
from subprocess import Popen
from sys import executable
####################  RULES  #####################
# 1- Make First Character of Global Variable CAPITAL
# 2- Leave at least 3 empty lines before and after a function, if it is not related with top or below functions
# 3- Use CAPITAL LETTERS for FUNCTION DEFINITION and start with "###"
# 4- Use "#" and start with capital letter while leaving a comment or explanation
##################################################

##############   COMPARE.PY NOTES   ##############
# Install openpyxl (pip install openpyxl)

### GLOBAL DEFINITIONS
Db_connection = sqlite3.connect("outputdb.sqlite")  
Config = configparser.RawConfigParser()


### FUNCTION DB - READ TABLENAMES
def tables_in_db() -> list:
    
    return sql_query_func("SELECT name AS \"Table Names in DB\"FROM sqlite_master  WHERE type='table'")["Table Names in DB"].to_list()



### FUNCTION SQL - READ SQL as DATAFRAME
def sql_query_func(sql_query:str) -> pandas.DataFrame :
    df_query_result = pandas.read_sql_query(sql_query , Db_connection)
    
    return df_query_result



### FUNCTION SQL - CONVERT DATAFRAME to STRING WOHI(WithOut Header and Index)
def sql_query_tostring_wohi(sql_query:str) -> str:
    df_result = sql_query_func(sql_query)
    
    return df_result.to_string(index=False , header=False)    
    
    

### FUNCTION SQL QUERY - GENERATES SELECT STATEMENT FOR ALL COLUMNS AND ONLY DIFFERENT COLUMNS, ALSO WHERE STATEMENTs
def sql_query_selects_and_where(table_name:str , old_folder_id:str , new_folder_id:str , exact_match_column_index = 0 , additional_sql_match=""):
    global Table_column_info , Columns_names
    
    Table_column_info = sql_query_func(f"PRAGMA table_info({table_name})") # Read table header information
    Columns_names = Table_column_info["name"].to_list()
    del Columns_names[:3] # Delete ID Output FolderId and Output FileId
    
    show_all_old_and_new_columns = str() # Show old and new columns together
    for column in Columns_names:
        replaced_column_name = str(column).replace("_" , " ")
        show_all_old_and_new_columns += f"new.{str(column)} AS \"NEW {replaced_column_name}\", old.{str(column)} AS \" OLD {replaced_column_name}\", "
    
    text_command = str()
    integer_command = str()
    major_column = str(Columns_names[exact_match_column_index]).replace("_" , " ")
    different_columnnames = [ f"new.{Columns_names[exact_match_column_index]} AS \"{major_column}\""] # Show only different columns
    sql_for_new_folder = f"SELECT * FROM {table_name} WHERE output_folder_id={new_folder_id}"
    sql_for_old_folder = f"SELECT * FROM {table_name} WHERE output_folder_id={old_folder_id}"
    
    for columnname in Columns_names[(exact_match_column_index+1):]:
        column_type = Table_column_info.loc[Table_column_info["name"] == columnname]["type"].to_string()
        
        replaced_column_name = str(columnname).replace("_" , " ")
        if "TEXT" in column_type:
            text_command += f" new.{columnname} == old.{columnname} AND"
            column_query_result = sql_query_func(f"""
                        SELECT 
                            new.{Columns_names[exact_match_column_index]}
                        FROM ({sql_for_new_folder}) new, ({sql_for_old_folder}) old 
                            WHERE
                            new.output_file_id == old.output_file_id AND 
                            new.{Columns_names[exact_match_column_index]} == old.{Columns_names[exact_match_column_index]} AND
                            NOT(new.{columnname} == old.{columnname})
            """)
            if column_query_result.empty:
                continue
            else:
                different_columnnames.append(f"old.{columnname} AS \" OLD {replaced_column_name}\", new.{columnname} AS \"NEW {replaced_column_name}\"")
            
            
        if "INTEGER" in column_type:
            
            if columnname in Percentage_use_list:
                integer_command += f" ((new.{columnname}  BETWEEN old.{columnname}*(100-{Percentage})/100 AND old.{columnname} *(100+{Percentage})/100) OR new.{columnname} == \"\" )  AND"
                column_query_result = sql_query_func(f"""
                        SELECT 
                            new.{Columns_names[exact_match_column_index]}
                        FROM ({sql_for_new_folder}) new, ({sql_for_old_folder}) old 
                            INNER JOIN Output_Folders ON Output_Folders.ID = new.output_folder_id
                            INNER JOIN Output_Filenames ON Output_Filenames.ID = new.output_file_id
                        WHERE
                            new.output_file_id == old.output_file_id AND     
                            new.{Columns_names[exact_match_column_index]} == old.{Columns_names[exact_match_column_index]} AND
                            NOT((new.{columnname}  BETWEEN old.{columnname}*(100-{Percentage})/100 AND old.{columnname} *(100+{Percentage})/100) OR new.{columnname} == \"\")
                            
                """)
                if column_query_result.empty:
                    continue
                else:
                    different_columnnames.append(f"old.{columnname} AS \" OLD {replaced_column_name}\", new.{columnname} AS \"NEW {replaced_column_name}\", (((new.{columnname}-old.{columnname})*100)/old.{columnname}) AS \"Change in Percentage(%)\"")
                continue
            
            if columnname in Session_state_list:
                integer_command += f" new.{columnname} >= old.{columnname} AND new.Service_Id == old.Service_Id AND"
                column_query_result = sql_query_func(f"""
                        SELECT 
                            new.{Columns_names[exact_match_column_index]}, old.{Columns_names[exact_match_column_index]} 
                        FROM ({sql_for_new_folder}) new, ({sql_for_old_folder}) old 
                            INNER JOIN Output_Folders ON Output_Folders.ID = new.output_folder_id
                            INNER JOIN Output_Filenames ON Output_Filenames.ID = new.output_file_id
                        WHERE
                            new.output_file_id == old.output_file_id AND     
                            new.{Columns_names[exact_match_column_index]} == old.{Columns_names[exact_match_column_index]} AND new.Service_Id == old.Service_Id AND
                            NOT(new.{columnname} >= old.{columnname})                          
                            
                """)        
                     
                
                if column_query_result.empty:
                    continue
                else:
                    different_columnnames.append(f"""
                                                 ((old.{columnname}/(24*3600)) || "d" || ((old.{columnname}%(24*3600))/3600) || "h" || (((old.{columnname}%(24*3600))%3600)/60) || "m" || (((old.{columnname}%(24*3600))%3600)%60) || "s")   AS \"OLD {columnname}\",
                                                 ((new.{columnname}/(24*3600)) || "d" || ((new.{columnname}%(24*3600))/3600) || "h" || (((new.{columnname}%(24*3600))%3600)/60) || "m" || (((new.{columnname}%(24*3600))%3600)%60) || "s")   AS \"NEW {columnname}\"
                                                 """)
                    print(different_columnnames)
                continue
            
                
                
            integer_command += f" new.{columnname} >= old.{columnname} AND"
            column_query_result = sql_query_func(f"""
                        SELECT 
                            new.{Columns_names[exact_match_column_index]}
                        FROM ({sql_for_new_folder}) new, ({sql_for_old_folder}) old 
                            INNER JOIN Output_Folders ON Output_Folders.ID = new.output_folder_id
                            INNER JOIN Output_Filenames ON Output_Filenames.ID = new.output_file_id
                        WHERE
                            new.output_file_id == old.output_file_id AND 
                            new.{Columns_names[exact_match_column_index]} == old.{Columns_names[exact_match_column_index]} AND
                            NOT(new.{columnname} >= old.{columnname})
                """)
            if column_query_result.empty:
                continue
            else:
                different_columnnames.append(f"old.{columnname} AS \" OLD {replaced_column_name}\", new.{columnname} AS \"NEW {replaced_column_name}\"")
     
    show_all_old_and_new_columns = show_all_old_and_new_columns[:-2]
     
    show_only_differet_columns_for_both = ", ".join(different_columnnames)

        
    text_command = text_command[:-3]
    integer_command = integer_command[:-3]
    
    sql_where_list = list()
    sql_where_list.append(text_command) if len(text_command) > 0 else None
    sql_where_list.append(integer_command) if len(integer_command) > 0 else None
        
    sql_where_statement = f"""
                                new.output_file_id == old.output_file_id AND 
                                new.{Columns_names[exact_match_column_index]} == old.{Columns_names[exact_match_column_index]} {additional_sql_match} AND 
                                NOT ({" AND ".join(sql_where_list)})"""
    
    return  show_all_old_and_new_columns , show_only_differet_columns_for_both , sql_where_statement 



### FUNCTION SQL QUERY - COMPARE EXISTING ITEMS
def compare_existing_items(table_name:str , old_folder_id:str , new_folder_id:str , display_type:str , where_statement , additional_column="" , order_by=""):
    sql_for_new_folder = f"SELECT * FROM {table_name} WHERE output_folder_id = {new_folder_id}"
    sql_for_old_folder = f"SELECT * FROM {table_name} WHERE output_folder_id = {old_folder_id}"
    
    compare_existing_items_result = sql_query_func(f"""
                        SELECT 
                            Output_Folders.Output_Foldername AS \"Output Folder Name\", 
                            Output_Filenames.Output_File AS \"File Name\", {additional_column}
                            {display_type} 
                        FROM ({sql_for_new_folder}) new, ({sql_for_old_folder}) old 
                            INNER JOIN Output_Folders ON Output_Folders.ID = new.output_folder_id
                            INNER JOIN Output_Filenames ON Output_Filenames.ID = new.output_file_id
                        WHERE
                            {where_statement}
                        {order_by}
                        """)
    
    if compare_existing_items_result.empty:
        return False
    else:
        return compare_existing_items_result
    
    

### FUNCTION SQL QUERY - FIND NEW ITEMS
def find_new_items(table_name:str , old_folder_id:str , new_folder_id:str , exact_match_column_index = 0 , additional_sql_match="" , order_by=""):
    sql_for_new_folder = f"SELECT * FROM {table_name} WHERE output_folder_id = {new_folder_id}"
    sql_for_old_folder = f"SELECT * FROM {table_name} WHERE output_folder_id = {old_folder_id}"
    
    replaced_header = ",".join(Columns_names).replace("_" , " ").split(",")
    new_file_columnnames = ", ".join(map("{0} AS \"{1}\"".format , Columns_names , replaced_header))
    
    new_items_result = sql_query_func(f"""
                            SELECT 
                                Output_Folders.Output_Foldername AS \"Output Folder Name\", 
                                Output_Filenames.Output_File AS \"File Name\", 
                                {new_file_columnnames} 
                            FROM ({sql_for_new_folder}) new
                                INNER JOIN Output_Folders ON Output_Folders.ID = new.output_folder_id 
                                INNER JOIN Output_Filenames ON Output_Filenames.ID = new.output_file_id 
                            WHERE
                                new.{Columns_names[exact_match_column_index]} NOT IN ( SELECT 
                                                                    old.{Columns_names[exact_match_column_index]} 
                                                                FROM ({sql_for_old_folder}) old 
                                                                WHERE 
                                                                    new.output_file_id == old.output_file_id {additional_sql_match}
                                                                    )
                            {order_by}
                        """)
    
    if new_items_result.empty:
        return False
    else:
        return new_items_result
    


### FUNCTION SQL QUERY - FIND MISSING ITEMS
def find_missing_items(table_name:str , old_folder_id:str , new_folder_id:str , exact_match_column_index = 0 , additional_sql_match="" , order_by=""):
    sql_for_new_folder = f"SELECT * FROM {table_name} WHERE output_folder_id = {new_folder_id}"
    sql_for_old_folder = f"SELECT * FROM {table_name} WHERE output_folder_id = {old_folder_id}"
    
    replaced_header = ",".join(Columns_names).replace("_" , " ").split(",")
    old_file_columnnames = ", ".join(map("{0} AS \"{1}\"".format , Columns_names , replaced_header))
    
    missing_items_result = sql_query_func(f"""
                            SELECT 
                                Output_Folders.Output_Foldername AS \"Output Folder Name\", 
                                Output_Filenames.Output_File AS \"File Name\", 
                                {old_file_columnnames} 
                            FROM ({sql_for_old_folder}) old
                                INNER JOIN Output_Folders ON Output_Folders.ID = old.output_folder_id 
                                INNER JOIN Output_Filenames ON Output_Filenames.ID = old.output_file_id 
                            WHERE
                                old.{Columns_names[exact_match_column_index]} NOT IN ( SELECT 
                                                                    new.{Columns_names[exact_match_column_index]} 
                                                                FROM ({sql_for_new_folder}) new 
                                                                WHERE 
                                                                    new.output_file_id == old.output_file_id {additional_sql_match}
                                                                    ) 
                            {order_by}
                        """)
    
    if missing_items_result.empty:
        return False
    else:
        return missing_items_result



####################################################################################################
####################################################################################################
####################                COMPARE              FUNCTIONS              ####################
####################################################################################################
####################################################################################################


### FUNCTINON COMPARE - SHOW ROUTER INTERFACE DETAIL    
def show_router_interface_detail(old_folder_id:str , new_folder_id:str) -> pandas.DataFrame:
    tablename = "show_router_interface_detail"
    Config.add_section(f"<strong>{tablename}</strong>")

    show_both_all_excel , show_both_difference_mail , where_statement = sql_query_selects_and_where(tablename , old_folder_id , new_folder_id)
    
    new_interfaces = find_new_items(tablename , old_folder_id , new_folder_id)
    if new_interfaces is not False:
        with pandas.ExcelWriter(Excel_output_name , mode = "a") as writer:      
            new_interfaces.to_excel(writer , sheet_name = f"router_interface_new" , index = False)
        Config.set(f"<strong>{tablename}</strong>" , "\n<span style=\"color: rgb(184, 49, 47);\">router_interface_new</span>" , f"\n{new_interfaces.to_html()}")
        
    missing_interfaces = find_missing_items(tablename , old_folder_id , new_folder_id)
    if missing_interfaces is not False:
        with pandas.ExcelWriter(Excel_output_name , mode = "a") as writer:      
            missing_interfaces.to_excel(writer , sheet_name = "router_interface_missing" , index = False)
        Config.set(f"<strong>{tablename}</strong>" , "\n<span style=\"color: rgb(184, 49, 47);\">router_interface_missing</span>" , f"\n{missing_interfaces.to_html()}")  
    
    compare_existing_interface_for_excel = compare_existing_items(tablename , old_folder_id , new_folder_id , show_both_all_excel , where_statement)
    if compare_existing_interface_for_excel is not False:
        with pandas.ExcelWriter(Excel_output_name , mode = "a") as writer:      
            compare_existing_interface_for_excel.to_excel(writer , sheet_name = "router_interface_changes" , index = False)
        compare_existing_interface_for_mail = compare_existing_items(tablename , old_folder_id , new_folder_id , show_both_difference_mail , where_statement)
        Config.set(f"<strong>{tablename}</strong>" , "\n<span style=\"color: rgb(184, 49, 47);\">router_interface_change</span>" , f"\n{compare_existing_interface_for_mail.to_html()}")
    
    with open('summary.log' , 'w+') as configfile:
        Config.write(configfile)
    


### FUNCTINON COMPARE - SHOW ROUTER BGP SUMMARY ALL    
def show_router_bgp_summary_all(old_folder_id:str , new_folder_id:str) -> pandas.DataFrame:
    tablename = "show_router_bgp_summary_all"
    Config.add_section(f"<strong>{tablename}</strong>")
    
    show_both_all_excel , show_both_difference_mail , where_statement = sql_query_selects_and_where(tablename , old_folder_id , new_folder_id , exact_match_column_index = 1 , additional_sql_match = f"AND new.Service_Id == old.Service_Id")

    serviceid = Columns_names[0]
    
    new_bgp_neighbors = find_new_items(tablename , old_folder_id , new_folder_id, exact_match_column_index = 1 , additional_sql_match = f"AND old.{serviceid} == new.{serviceid}")
    if new_bgp_neighbors is not False:
        with pandas.ExcelWriter(Excel_output_name , mode = "a") as writer:      
            new_bgp_neighbors.to_excel(writer , sheet_name = f"router_bgp_neighbor_new" , index = False)
        Config.set(f"<strong>{tablename}</strong>" , "\n<span style=\"color: rgb(184, 49, 47);\">router_bgp_neighbor_new</span>" , f"\n{new_bgp_neighbors.to_html()}")
    
    
    missing_bgp_neighbors = find_missing_items(tablename , old_folder_id , new_folder_id , exact_match_column_index = 1 , additional_sql_match = f"AND old.{serviceid} == new.{serviceid}")
    if missing_bgp_neighbors is not False:
        with pandas.ExcelWriter(Excel_output_name , mode = "a") as writer:      
            missing_bgp_neighbors.to_excel(writer , sheet_name = "router_bgp_neighbor_missing" , index = False)
        Config.set(f"<strong>{tablename}</strong>", "\n<span style=\"color: rgb(184, 49, 47);\">router_bgp_neighbor_missing</span>", f"\n{missing_bgp_neighbors.to_html()}")  
    
    compare_existing_bgp_neighbors_for_excel = compare_existing_items(tablename , old_folder_id , new_folder_id , show_both_all_excel , where_statement , order_by = f"ORDER BY new.{serviceid}")
    if compare_existing_bgp_neighbors_for_excel is not False:
        with pandas.ExcelWriter(Excel_output_name , mode = "a") as writer:      
            compare_existing_bgp_neighbors_for_excel.to_excel(writer , sheet_name = "router_bgp_neighbors_changes" , index = False)
        compare_existing_bgp_neighbors_for_mail = compare_existing_items(tablename , old_folder_id , new_folder_id , show_both_difference_mail , where_statement , additional_column = f"new.{serviceid}," , order_by = f"ORDER BY new.{serviceid}")
        Config.set(f"<strong>{tablename}</strong>" , "\n<span style=\"color: rgb(184, 49, 47);\">router_bgp_neighbors_change</span>" , f"\n{compare_existing_bgp_neighbors_for_mail.to_html()}")
    
    
    with open('summary.log', 'w+') as configfile:
        Config.write(configfile)
    
    
    

####################################################################################################
####################################################################################################
####################                       MAIN FUNCTION                       ####################
####################################################################################################
####################################################################################################
def main():
    global Excel_output_name , Percentage , Percentage_use_list , Session_state_list
    
    Percentage_use_list = [ "Family_Ipv4_Rec", "Family_Ipv4_Act", "Family_Ipv4_Sent",
                            "Family_Ipv6_Rec", "Family_Ipv6_Act", "Family_Ipv6_Sent",
                            "Family_Vpnipv4_Rec", "Family_Vpnipv4_Act", "Family_Vpnipv4_Sent",
                            "Family_Vpnipv6_Rec","Family_Vpnipv6_Act","Family_Vpnipv6_Sent",
                            "Family_Mvpnipv4_Rec","Family_Mvpnipv4_Act","Family_Mvpnipv4_Sent",
                            "Family_Routetarget_Rec","Family_Routetarget_Act","Family_Routetarget_Sent",
                            "Family_Mvpnipv6_Rec","Family_Mvpnipv6_Act","Family_Mvpnipv6_Sent",
                            "Family_Evpn_Rec","Family_Evpn_Act","Family_Evpn_Sent",
                            "Family_Label_Ipv4_Rec", "Family_Label_Ipv4_Act", "Family_Label_Ipv4_Sent",
                            "Family_Label_Ipv6_Rec", "Family_Label_Ipv6_Act", "Family_Label_Ipv6_Sent" ] # Use header name in DB
    
    Session_state_list = [ "Updown_Time"]
    
    first_folder_id = 1    
    latest_folder_id = sql_query_tostring_wohi("SELECT MAX(ID) FROM Output_Folders")
    
    if latest_folder_id != "1":
        previous_folder_id = str(int(latest_folder_id)-1)
    else:
        previous_folder_id = first_folder_id
    
    
    available_function_list = list()
    read_compare_file = open(f"compare.py" , "r")
    compare_file_lines = read_compare_file.readlines()
    for line_of_compare in compare_file_lines:
        if line_of_compare.startswith("def show"):
            stripped_functionname = line_of_compare.strip().removeprefix("def ").split("(")[0]
            if stripped_functionname in tables_in_db():
                available_function_list.append(stripped_functionname)
    read_compare_file.close()
    availabe_compare_functions = pandas.DataFrame(available_function_list,columns=["Available Compare Functions"])
        
    # Create new xslx after each compare
    Output_db_sql = f"outputdb.sqlite"
    Db_modified_time = str(ctime(os.path.getmtime(Output_db_sql)).replace(":" , ""))
     
    if os.path.isdir("email_attachments") == False:
        os.mkdir("email_attachments")
    Excel_output_name = f"email_attachments\\changes_in_outputs_{Db_modified_time}.xlsx"

    availabe_compare_functions.to_excel(Excel_output_name ,"Available Compare Functions")
    Config.read("init.cfg")
    Percentage = Config.get("Compare" , "percentage")
    Config.clear()
    
    
    for function in available_function_list:
        function_run = globals()[function]
        function_run(previous_folder_id , latest_folder_id)

main()
Popen([executable , "send_email.py"])

Db_connection.close()
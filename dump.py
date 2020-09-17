# IMPORTS ==============================================================================================================
import urllib.request, urllib.error, urllib.parse
import json
import os

# CONSTANTS ============================================================================================================
BASE_ALEXA_SITE =       "https://www.alexa.com"
STRING_NO_SUBCATEG =    "_Most_popular_"
SUBCATEG_TITLE_BEGIN =  "<div class=\"categories"
SUBCATEG_TITLE_END =    "</section>"
SUBCATEG_ITEM_BEGIN =   "<li><a href=\""
SUBCATEG_ITEM_END =     "</a> <span class=\"small gray\""
SUBCATEG_ITEM_SPLIT =   "\">"
SITE_ITEM_BEGIN_0 =     "<div class=\"tr site-listing\">"
SITE_ITEM_END_0 =       "</p>"
SITE_ITEM_BEGIN_1 =     "<a href=\"/siteinfo/"
SITE_ITEM_END_1 =       "\">"
FILE_OUTPUT =           "data.json"
LOCAL_PATH_PREFIX =     "./"
THRESHOLD_TO_SAVE =     100

# FUNCTIONS ============================================================================================================
def web_page_to_text(url):
    text_return = ""
    try:
        response = urllib.request.urlopen(url)
        text_return = response.read().decode("utf-8")
    except KeyboardInterrupt:
        exit()
    except:
        pass
    return text_return

def alexa_get_subcateg_offline(content):
    list_subcateg = []
    position = content.find(SUBCATEG_TITLE_BEGIN)
    if position != -1:
        content = content[position:-1]
        position = content.find(SUBCATEG_TITLE_END) + + len(SUBCATEG_TITLE_END)
        content = content[0:position]
        while content.find(SUBCATEG_ITEM_BEGIN) != -1:
            position = content.find(SUBCATEG_ITEM_BEGIN) + len(SUBCATEG_ITEM_BEGIN)
            content = content[position:-1]
            position = content.find(SUBCATEG_ITEM_END)
            list_subcateg.append(content[0:position].split(SUBCATEG_ITEM_SPLIT)[0])
    return list_subcateg

def alexa_get_sites_offline(content):
    list_sites = []
    while content.find(SITE_ITEM_BEGIN_0) != -1:
        position = content.find(SITE_ITEM_BEGIN_0) + len(SITE_ITEM_BEGIN_0)
        content = content[position:-1]
        position = content.find(SITE_ITEM_END_0)
        raw_item = content[0:position]
        position = raw_item.find(SITE_ITEM_BEGIN_1) + len(SITE_ITEM_BEGIN_1)
        raw_item = raw_item[position:-1]
        position = raw_item.find(SITE_ITEM_END_1)
        raw_item = raw_item[0:position]
        list_sites.append(raw_item)
    return list_sites

def open_creating_dirs(path, mode):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    fp_itemx = open(path, mode)
    return fp_itemx

# MAIN SCRIPT ==========================================================================================================
# Output file initialization
if os.path.exists(FILE_OUTPUT):
    fp_json = open(FILE_OUTPUT, "r")
    output_data = json.load(fp_json)
else:
    output_data = {}
    fp_json = open(FILE_OUTPUT, "w")
    json.dump(output_data, fp_json)
fp_json.close()
# Controls
dont_stress_the_disk = 0
always_increment = 0
visited_list = []
# Stack as list
list_to_explore = ["/topsites/category/Top"]
#Depth first algorithm
while len(list_to_explore) > 0:
    item_to_explore = list_to_explore.pop(0) #Stack control using always 0
    if item_to_explore not in visited_list:
        visited_list.append(item_to_explore)
        # Verify json insertion
        item_hierarchy = item_to_explore.split("/")
        item_hierarchy.remove("")
        is_item_already_in_json = True
        curr_dict = output_data
        for key_name in item_hierarchy:
            if key_name not in curr_dict.keys():
                is_item_already_in_json = False
                break
            else:
                curr_dict = curr_dict[key_name]
        if is_item_already_in_json and len(curr_dict.keys()) > 0:
            explored_subcateg = []
            for subcateg_name in curr_dict.keys():
                explored_subcateg.append(item_to_explore + "/" + subcateg_name)
            list_to_explore = explored_subcateg + list_to_explore
        else:
            local_path = LOCAL_PATH_PREFIX + item_to_explore[1:] + ".html"
            always_increment += 1
            print("")
            print("Exploring: " + item_to_explore)
            print("List size: " + str(len(list_to_explore)))
            print("Total nodes: " + str(always_increment))
            #Verify file download
            if os.path.exists(local_path) and os.stat(local_path).st_size != 0:
                fp_item = open(local_path, "r")
                print("Available offline")
            else:
                print("Downloading")
                text_buffer = web_page_to_text(BASE_ALEXA_SITE + item_to_explore) 
                try:
                    fp_item = open_creating_dirs(local_path, "w")
                    fp_item.write(text_buffer)
                except: #Uninterruptable write
                    pass
                fp_item.close()
                fp_item = open(local_path, "r")
            text_buffer = fp_item.read()
            fp_item.close()
            # Parses HTML
            explored_subcateg = alexa_get_subcateg_offline(text_buffer)
            explored_sites = alexa_get_sites_offline(text_buffer)
            curr_dict = output_data
            # Selects point in output dictionary
            for i in range(len(item_hierarchy) - 1):
                if item_hierarchy[i] not in curr_dict.keys():
                    curr_dict[item_hierarchy[i]] = {}
                curr_dict = curr_dict[item_hierarchy[i]]
            # Handles the number of subcategories
            if len(explored_subcateg) > 0:
                curr_dict[item_hierarchy[-1]] = {}
                curr_dict = curr_dict[item_hierarchy[-1]]
                for subcateg_path in explored_subcateg:
                    curr_dict[subcateg_path.split("/")[-1]] = {}
                curr_dict[STRING_NO_SUBCATEG] = explored_sites
                list_to_explore = explored_subcateg + list_to_explore
            else:
                curr_dict[item_hierarchy[-1]] = explored_sites
            # Writes to output file with control
            dont_stress_the_disk += 1
            if dont_stress_the_disk >= THRESHOLD_TO_SAVE:
                fp_json = open(FILE_OUTPUT, "w")
                json.dump(output_data, fp_json)
                fp_json.close()

# Writes final result anyway
fp_json = open(FILE_OUTPUT, "w")
json.dump(output_data, fp_json)
fp_json.close()

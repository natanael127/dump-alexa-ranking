# IMPORTS ==============================================================================================================
import urllib.request, urllib.error, urllib.parse
import json
import os

# CONSTANTS ============================================================================================================
BASE_ALEXA_SITE =       "https://www.alexa.com"
SUBCATEG_TITLE_BEGIN =  "<div class=\"categories"
SUBCATEG_TITLE_END =    "</section>"
SUBCATEG_ITEM_BEGIN =   "<li><a href=\""
SUBCATEG_ITEM_END =     "</a> <span class=\"small gray\""
SUBCATEG_ITEM_SPLIT =   "\">"
SITE_ITEM_BEGIN_0 =     "<div class=\"tr site-listing\">"
SITE_ITEM_END_0 =       "</p>"
SITE_ITEM_BEGIN_1 =     "<a href=\"/siteinfo/"
SITE_ITEM_END_1 =       "\">"
FILE_TO_SAVE =          "data.json"
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

def alexa_get_subcateg(sufix):
    content = web_page_to_text(BASE_ALEXA_SITE + sufix)
    alexa_get_subcateg_offline(content)

def alexa_get_sites(sufix):    
    content = web_page_to_text(BASE_ALEXA_SITE + sufix)
    alexa_get_sites_offline(content)

def open_creating_dirs(path, mode):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    fpx = open(path, mode)
    return fpx

# MAIN SCRIPT ==========================================================================================================
# Control
dont_stress_the_disk = 0
always_increment = 0
# Stack as list
list_to_explore = ["/topsites/category/Top"]
#Depth first algorithm
while len(list_to_explore) > 0:
    item_to_explore = list_to_explore.pop(0) #Stack control
    local_path = LOCAL_PATH_PREFIX + item_to_explore[1:] + ".html"
    always_increment += 1
    print("")
    print("Exploring: " + item_to_explore)
    print("List size: " + str(len(list_to_explore)))
    print("Total nodes: " + str(always_increment))
    if os.path.exists(local_path) and os.stat(local_path).st_size != 0:
        fp = open(local_path, "r")
    else:
        text_buffer = web_page_to_text(BASE_ALEXA_SITE + item_to_explore) 
        try:
            fp = open_creating_dirs(local_path, "w")
            fp.write(text_buffer)
        except: #Uninterruptable write
            pass
        fp.close()
        fp = open(local_path, "r")
    explored_result = alexa_get_subcateg_offline(fp.read())
    fp.close()
    if len(explored_result) != 0:
        list_to_explore = explored_result + list_to_explore


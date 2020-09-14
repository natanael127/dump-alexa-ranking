#TODO: interpret root categories

import urllib.request, urllib.error, urllib.parse
import json

BASE_ALEXA_SITE =       "https://www.alexa.com"
SUBCATEG_TITLE_BEGIN =  "<a class=\"catList open\">Sub-Categories"
SUBCATEG_TITLE_END =    "</section>"
SUBCATEG_ITEM_BEGIN =   "<li><a href=\""
SUBCATEG_ITEM_END =     "</a> <span class=\"small gray\""
SUBCATEG_ITEM_SPLIT =   "\">"
SITE_ITEM_BEGIN_0 =     "<div class=\"tr site-listing\">"
SITE_ITEM_END_0 =       "</p>"
SITE_ITEM_BEGIN_1 =     "<a href=\"/siteinfo/"
SITE_ITEM_END_1 =       "\">"
FILE_TO_SAVE =          "data.json"
THRESHOLD_TO_SAVE =     100

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

def alexa_get_subcateg_page(sufix):
    list_subcateg = []
    content = web_page_to_text(BASE_ALEXA_SITE + sufix)
    position = content.find(SUBCATEG_TITLE_BEGIN)
    if position != -1:
        content = content[position:-1]
        position = content.find(SUBCATEG_TITLE_END) + + len(SUBCATEG_TITLE_END)
        content = content[0:position]
        while content.find(SUBCATEG_ITEM_BEGIN) != -1:
            position = content.find(SUBCATEG_ITEM_BEGIN) + len(SUBCATEG_ITEM_BEGIN)
            content = content[position:-1]
            position = content.find(SUBCATEG_ITEM_END)
            list_subcateg.append(tuple(content[0:position].split(SUBCATEG_ITEM_SPLIT)))
    return list_subcateg

def alexa_get_sites_page(sufix):
    list_sites = []
    content = web_page_to_text(BASE_ALEXA_SITE + sufix)
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

fp = open(FILE_TO_SAVE, "r")
all_data = json.load(fp)
fp.close()
dont_stress_the_disk = 0
list_to_explore = [("/topsites/category/Top/Games/Video_Games", "Video Games"), ("/topsites/category/Top/Games/Yard,_Deck,_and_Table_Games", "Yard, Deck, and Table Games")]

while len(list_to_explore) > 0:
    item_to_explore = list_to_explore.pop(0)
    print("List size: " + str(len(list_to_explore)) + " ||| Exploring: " + item_to_explore[0])
    explored_result = alexa_get_subcateg_page(item_to_explore[0])
    if len(explored_result) == 0:
        hierarchical_key_list = item_to_explore[0].split("/")
        hierarchical_key_list.remove("")
        curr_dict = all_data
        for i in range(len(hierarchical_key_list)):
            if hierarchical_key_list[i] not in curr_dict.keys():
                if i == len(hierarchical_key_list) - 1:
                    curr_dict[hierarchical_key_list[i]] = alexa_get_sites_page(item_to_explore[0])
                else:
                    curr_dict[hierarchical_key_list[i]] = {}
            curr_dict = curr_dict[hierarchical_key_list[i]] #Shallow copy
        dont_stress_the_disk += 1
        if dont_stress_the_disk >= THRESHOLD_TO_SAVE:
            dont_stress_the_disk = 0
            fp = open(FILE_TO_SAVE, "w")
            json.dump(all_data, fp)
            fp.close()
    else:
        list_to_explore = explored_result + list_to_explore


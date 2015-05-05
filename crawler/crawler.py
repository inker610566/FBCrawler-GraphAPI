import sys
sys.path.append("../secret")
from access_token import access_token
from os

Query_base = "https://graph.facebook.com/v2.3";

def CrawlGroup(group_id, group_name):
    try
	os.mkdir(group_name)
    except OSError:
	pass

    os.chdir(group_name)

    (dirpath, dirnames, filenames) = next(os.walk("."))
    
    
    









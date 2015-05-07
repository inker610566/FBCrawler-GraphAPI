import sys
sys.path.append("../secret")
from secret.access_token import access_token
import os
from datetime import date as Date
from datetime import timedelta as Timedelta
import re
import json

Query_base = "https://graph.facebook.com/v2.3";

def getLastCrawlDate():
    (dirpath, dirnames, filenames) = next(os.walk("."))
    if filenames:
        # 2015-01-01.json
        mxDate = max(filenames)
        res = re.match("^(\\d{4})-(\\d{2})-(\\d{2})\\.json$", mxDate)
        assert res
        return Date(year=int(res.group(1)), month=int(res.group(2)), day=int(res.group(3)))
    else:
        return Date(year=2015, month=1, day=1)
    
def xrange(start, end, step):
    while start < end:
        yield start
        start += step

def Curl(url, filename):
    print "..\\curl --insecure \"%s\" > %s"%(url, filename)
    exitCode = os.system("..\\curl --insecure \"%s\" > %s"%(url, filename))
    assert exitCode == 0

def Jsonfile2Object(filename):
    fp = open(filename, "r")
    obj = json.load(fp)
    fp.close()
    return obj

def Url2Object(url):
    TMP_JSON_FILE = "log\\tmp.json"

    Curl(url, TMP_JSON_FILE)
    return Jsonfile2Object(TMP_JSON_FILE)

def has_path(json_obj, path):
    for node in path:
	if json_obj.has_key(node):
	   json_obj = json_obj[node]
	else:
	   return False
    return True

def CrawlGroupDate(group_id, date):

    # first query
    query = (Query_base + "/%s/feed?since=%s&until=%s&access_token=%s&fields=from,to,created_time,updated_time,likes.limit(0).summary(true),comments,link,name,picture,message") % (
        group_id,
        date.strftime("%Y-%m-%d"),
        (date + Timedelta(days=1)).strftime("%Y-%m-%d"),
        access_token
    )
    
    Datas = []

    while True:
	# read json
	curjson = Url2Object(query)

	# expand comments
	for post in curjson["data"]:
	    if has_path(post, ("comments", "paging", "next")):
		comments = post["comments"]["data"]
		next_query = post["comments"]["paging"]["next"]

		while True:
		    comment = Url2Object(next_query)
		    if not has_path(comment, ("data",)) or len(comment["data"]) == 0:
			break
		    comments.extend(comment["data"])
		    if not has_path(comment, ("paging", "next")):
			break
		    next_query = comment["paging"]["next"]
		    
	
        if curjson["data"]:
            Datas.extend(curjson["data"])
        else:
            break

        query = curjson["paging"]["next"]

    return Datas


def CrawlGroup(group_id, group_name):
    # mkdir group json dir
    try:
	os.mkdir(group_name)
    except OSError:
	pass

    os.chdir(group_name)

    # mkdir log dir
    try:
	os.mkdir("log")
    except OSError:
	pass

    for tarDate in xrange(getLastCrawlDate(), Date.today() + Timedelta(days=1), Timedelta(days=1)):
        # crawl tarDate
	posts = CrawlGroupDate(group_id, tarDate)
	if posts:
	    fp = open(tarDate.strftime("%Y-%m-%d")+".json", "w")
	    fp.write(json.dumps(posts))
	    fp.close()
    
    os.chdir("..")






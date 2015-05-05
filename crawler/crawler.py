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
    print "curl \"%s\" > %s"%(url, filename)
    exitCode = os.system("..\\curl --insecure \"%s\" > %s"%(url, filename))
    assert exitCode == 0

def CrawlGroupDate(group_id, date):

    # first query
    query = (Query_base + "/%s/feed?since=%s&until=%s&access_token=%s") % (
        group_id,
        date.strftime("%Y-%m-%d"),
        (date + Timedelta(days=1)).strftime("%Y-%m-%d"),
        access_token
    )
    
    TMP_JSON_FILE = "log\\tmp.json"

    Datas = []

    while True:
        Curl(query, TMP_JSON_FILE)
        fp = open(TMP_JSON_FILE, "r")
        curjson = json.load(fp)
        fp.close()
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

    for tarDate in xrange(getLastCrawlDate(), Date.today(), Timedelta(days=1)):
        # crawl tarDate
	posts = CrawlGroupDate(group_id, tarDate)
	if posts:
	    fp = open(tarDate.strftime("%Y-%m-%d")+".json", "w")
	    fp.write(json.dumps(posts))
	    fp.close()
    
    os.chdir("..")






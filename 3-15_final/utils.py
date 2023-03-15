import os
import traceback
from datetime import date, datetime
from github import GithubException, Github, RateLimitExceededException


def mkdir(path):
	folder = os.path.exists(path)
	if not folder:                   
		os.makedirs(path)            
		print("---  mkdir: " + path + "  ---")
	else:
		print("---  There is this folder: " + path + "  ---")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


skip_status = ["400","404","409","block"]
too_large = "The history or contributor list is too large to list contributors for this repository via the API"


"""
400: No URL
403: Ratelimit, block, too large
404: Not Found
409: Empty exception
"""
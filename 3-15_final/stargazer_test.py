from github import Github
import json
from datetime import date, datetime
import pprint
from repo_feature_crawler import get_repo_feature

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# new valid token
access_token = "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"

g = Github(login_or_token=access_token)

# repo = g.get_repo("intel-analytics/BigDL")
# sdate = repo.get_stargazers_with_dates()
# stargazers = {}
# for s in sdate:
#     stargazers[s.user.id] = s.starred_at

# jsonObj = json.dumps(stargazers,default=json_serial,indent=4)
# f = open('new_json.json', 'w')
# f.write(jsonObj)
# f.close()

# comp = ['pivotal', 'github', 'redhat-developer', 'square', 'groupon', 'Yelp', 'zynga', 'Juniper']

# repo = g.get_repo("AndyLuo1029/CI")


# writer = open('233.json','w')
# rec = [{'GHA': {}}, {'Travis': {}}, {'CircleCI': {}}, {'AppVeyor': {}}, {'Azure': {}}, {'GitLab': {}}, {'Jenkins': {}}]
# jsonObj = json.dumps(dict(zip('CI_commmits',rec)),indent=4, default=json_serial, separators=(',', ': '), ensure_ascii=False)
# writer.write(jsonObj)
# writer.close()

repo = g.get_repo('linkedin/kafka')
get_repo_feature(repo)
import time
import json
import random
from github import Github, RateLimitExceededException, GithubException
from requests import ReadTimeout, exceptions
from socket import timeout
from datetime import date, datetime

access_token = "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"

g = Github(login_or_token=access_token)

comp = ['linkedin', 'facebook', 'google', 'amzn', 'youtube', 'pinterest', 'apple', 'oracle', 'intel', 'IBM', 'vmware', 'Netflix', 'salesforce', 'dell', 'Medium', 'tripadvisor', 'dropbox', 'JetBrains', 'pivotal', 'github', 'redhat-developer', 'square', 'groupon', 'Yelp', 'zynga', 'Juniper', 'docker', 'tenable', 'okta', 'cisco', 'paypal', 'eBay', 'yahoo', 'twitter', 'NVIDIA', 'Mastercard', 'HewlettPackard', 'nutanix', 'aol', 'docusign', 'Mirantis', 'alibaba', 'Tencent', 'baidu', 'bilibili', 'ctripcorp', 'qunarcorp', 'douban', 'NetEase', 'jobbole', 'vipshop', 'zhihu', 'Qihoo360', 'weibocom', 'HujiangTechnology', 'meitu', 'iuap-design', 'yued-fe', 'baixing', 'anjuke', 'lingochamp', 'Coding', 'haiwen', 'jpush', 'bytedance', 'meili', 'easemob', 'yyued', 'qiniu', 'linuxdeepin', 'xitu', 'iqiyi', 'FacePlusPlus', 'CodisLabs', 'citrix', 'airbnb', 'Instagram', 'uber', 'youzan', 'Meituan-Dianping', 'eleme', 'XiaoMi', 'Huawei', 'didi']

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def get_org_feature(org, org_writer):
    """
        Get a single orgnization's feature, will store all orgnizations' features into one JSON file.
    """
# deleted features which always return None: company total_private_repos collaborators private_gists owned_private_repos disk_usage 
    features_title = ['name','id','created_at','updated_at','login','type','followers',
                      'following','public_gists','repo_count','public_repos','members','public_members']

    features = [org.name, org.id, org.created_at, org.updated_at, org.login, org.type, org.followers, org.following, org.public_gists]
    repos = org.get_repos()
    repo_count = 0 if (str(type(repos))=="<class \'NoneType\'>") else repos.totalCount
    features.extend([repo_count, org.public_repos])
    members = 0 if(str(type(org.get_members()))=="<class \'NoneType\'>") else org.get_members().totalCount
    public_members = 0 if(str(type(org.get_public_members()))=="<class \'NoneType\'>") else org.get_public_members().totalCount
    features.extend([members, public_members])
    jsonObj = json.dumps(dict(zip(features_title,features)),indent=4, default=json_serial, separators=(',', ': '), ensure_ascii=False)
    org_writer.write(jsonObj)
    
    """
    company features:
        name
        id
        created_at
        updated_at
        login
        type
        followers
        following
        public_gists
        get_repos
        public_repos
        get_members totalCount
        get_public_members totalCount
    """
if __name__ == '__main__':
    f = open('org.json','w')
    for c in comp:
        flag_timeout = 0
        org = g.get_organization(c)
        try:
            get_org_feature(org,f)
        except RateLimitExceededException:
            RStime = Github(access_token).rate_limiting_resettime
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
            get_org_feature(org,f)
        except (ReadTimeout, timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1
            get_org_feature(org,f)
        except GithubException as r:
            print("GithubException:")
            print(r,r.args)
            time.sleep(60)
            print(time.strftime("GithubException: [%H:%M] Get back to work!", time.localtime()))
            get_org_feature(org,f)
        except exceptions as r:
            print("Requests Exceptions:")
            print(r,r.args)
            time.sleep(60)
            get_org_feature(org,f)
    f.close()
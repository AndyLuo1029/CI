import time
import csv
from github import Github, RateLimitExceededException, GithubException
from requests import ReadTimeout
from socket import timeout

access_token = "your token"

g = Github(login_or_token=access_token,per_page=100)

csvfile = open("/root/Juntao/Test_"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+".csv","a")
w = csv.writer(csvfile)
# write the head row
w.writerow(['repo_full_name','id','URL','stars','git_num_commits','git_num_contributors',
'is_fork','language','created_at','issue_comments_num','commit_comments_num','pr_comments_num',
'pr_num','archived','default_branch','forks','forks_count','has_downloads','has_issues','has_pages',
'has_projects','has_wiki','homepage','network_count','open_issues','open_issues_count','organization_name',
'owner_name','parent_name','permissions_admin','permissions_maintain','permissions_pull','permissions_push',
'permissions_triage','private','pushed_at','size','source_name','subscribers_count','updated_at','watchers','watchers_count'])

def get_repos(token,stars,round):
    global g,w
    try:
        # get top 10,000 popular repos  
        # while round < 10:
        flag_timeout = 0
        q = "stars:1.."+str(stars)
        repos = g.search_repositories(query=q,sort="stars",order="desc")
        print('Get repos succefully, now in round:'+str(round))

        cnt = 1
        for repo in repos:
            #write repo's attribute
            stars = repo.stargazers_count

            org_name = 'NoneType' if(str(type(repo.organization))=="<class \'NoneType\'>") else repo.organization.name
            owner_name = 'NoneType' if(str(type(repo.owner))=="<class \'NoneType\'>") else repo.owner.name
            parent_name = 'NoneType' if(str(type(repo.parent))=="<class \'NoneType\'>") else repo.parent.name
            source_name = 'NoneType' if(str(type(repo.source))=="<class \'NoneType\'>") else repo.source.name

            reco = [repo.name,repo.id,repo.url,repo.stargazers_count,repo.get_commits().totalCount,repo.get_contributors().totalCount,
            repo.fork,repo.language,repo.created_at,repo.get_issues_comments().totalCount,repo.get_comments().totalCount,repo.get_pulls_comments().totalCount,
            repo.get_pulls().totalCount,repo.archived,repo.default_branch,repo.forks,repo.forks_count,repo.has_downloads,repo.has_issues,repo.has_pages,
            repo.has_projects,repo.has_wiki,repo.homepage,repo.network_count,repo.open_issues,repo.open_issues_count,org_name,owner_name,parent_name,repo.permissions.admin,
            repo.permissions.maintain,repo.permissions.pull,repo.permissions.push,repo.permissions.triage,repo.private,repo.pushed_at,repo.size,source_name,repo.subscribers_count,
            repo.updated_at,repo.watchers,repo.watchers_count]
            print("writing:"+str(cnt))
            w.writerow(reco)
            cnt += 1
        w.writerow(['#']) 
        print("Round END!")
        round += 1 
    except RateLimitExceededException:
        RStime = Github(token).rate_limiting_resettime
        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
        print("limiting:"+str(g.rate_limiting))
        print("search"+str(g.get_rate_limit().search))
        stime = RStime-time.time()+0.5
        if stime>0:
            time.sleep(stime)
        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        w.writerow(['!!!']) 
        return get_repos(token,stars,round)
    except (ReadTimeout, timeout) as e:
        flag_timeout+=1
        if flag_timeout==5:
            print("Please check network connection.")
        print("Read Timeout... Sleep 1 min.")
        time.sleep(60)
        print("Try again.")
        flag_timeout -= 1
    except GithubException as r:
        print(repo.full_name)
        print(r,r.args)
        return get_repos(token,stars,round)

if __name__ == '__main__':
    max_star = 400000
    start_round = 0
    print("start...")
    get_repos(access_token,max_star,start_round)
    csvfile.close()
    print('the end')


# Get a specific content file
# repo = g.get_repo("AndyLuo1029/BigDL")
# contents = repo.get_contents("docs/readthedocs/source/_static/js/chronos_installation_guide.js")
# print("contents:"+str(contents)+'\n')

# Get all of the contents of the repository recursively
# repo = g.get_repo("PyGithub/PyGithub")
# contents = repo.get_contents("")
# while contents:
#      file_content = contents.pop(0)
#      if file_content.type == "dir":
#          contents.extend(repo.get_contents(file_content.path))
#      else:
#          print(file_content)
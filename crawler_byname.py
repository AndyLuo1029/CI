import time
import csv
import re
from github import Github, RateLimitExceededException, GithubException
from requests import ReadTimeout
from socket import timeout

access_token = "token"

g = Github(login_or_token=access_token)

# use regEx to get company name and repos
f = open("companies.md")
md = f.read()
f.close()
repos = re.findall(r'\'.*\'',md)

all = []
for r in repos:
    comp_repos = r.replace("\'","").replace(" ","")
    all.extend(comp_repos.split(','))

cnt = 0

csvfile = open("Test_"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+".csv","a")
w = csv.writer(csvfile)
# write the head row
w.writerow(['repo_full_name','id','URL','stars','git_num_commits','git_num_contributors','is_fork','language','created_at',
'issue_comments_num','commit_comments_num','pr_comments_num','pr_num','archived','default_branch','forks_count','homepage',
'network_count','open_issues','open_issues_count','organization_name','owner_name','parent_name','private','pushed_at',
'size','source_name','subscribers_count','updated_at','watchers_count','GHA','Travis'])

def get_repo():
    global g, w, all, cnt
    while(cnt<len(all)):
        try:
            flag_timeout = 0
            now_repo = all[cnt]
            repo = g.get_repo(now_repo)
            print('Get repo succefully:'+now_repo+','+str(cnt))
            cnt+=1

            org_name = 'NoneType' if(str(type(repo.organization))=="<class \'NoneType\'>") else repo.organization.name
            owner_name = 'NoneType' if(str(type(repo.owner))=="<class \'NoneType\'>") else repo.owner.name
            parent_name = 'NoneType' if(str(type(repo.parent))=="<class \'NoneType\'>") else repo.parent.name
            source_name = 'NoneType' if(str(type(repo.source))=="<class \'NoneType\'>") else repo.source.name
            
            has_GHA = False
            has_Travis = False
            has_CircleCI = False
            has_AppVeyor = False
            has_Azure = False
            has_GitLab = False
            has_Jenkins = False
            try:
                GHA_Files = repo.get_contents("/.github/workflows")
                for con in GHA_Files:
                    if(".yml" in str(con.name)):
                        has_GHA = True
                        break
            except GithubException as r:
                pass

            try:
                repo.get_contents("/.travis.yml")
                has_Travis = True
            except GithubException as r:
                pass

            try:
                repo.get_contents("/.circleci/config.yml")
                has_CircleCI = True
            except GithubException as r:
                pass

            try:
                repo.get_contents("/appveyor.yml")
                has_AppVeyor = True
            except GithubException as r:
                pass

            try:
                repo.get_contents("/azure-pipelines.yml")
                has_Azure = True
            except GithubException as r:
                pass

            try:
                repo.get_contents("/.gitlab-ci.yml")
                has_GitLab = True
            except GithubException as r:
                pass

            try:
                repo.get_contents("/Jenkinsfile")
                has_Jenkins = True
            except GithubException as r:
                pass

            reco = [repo.name,repo.id,repo.url,repo.stargazers_count,repo.get_commits().totalCount,repo.get_contributors().totalCount,
            repo.fork,repo.language,repo.created_at,repo.get_issues_comments().totalCount,repo.get_comments().totalCount,
            repo.get_pulls_comments().totalCount,repo.get_pulls().totalCount,repo.archived,repo.default_branch,repo.forks_count,
            repo.homepage,repo.network_count,repo.open_issues,repo.open_issues_count,org_name,owner_name,parent_name,
            repo.private,repo.pushed_at,repo.size,source_name,repo.subscribers_count,repo.updated_at,repo.watchers_count,has_GHA,has_Travis]

            print("writing")
            w.writerow(reco)
        except RateLimitExceededException:
            RStime = Github(access_token).rate_limiting_resettime
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
            return get_repo()
        except (ReadTimeout, timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
            print("Read Timeout... Sleep 1 min.")
            time.sleep(60)
            print("Try again.")
            flag_timeout -= 1
        except GithubException as r:
            print(now_repo)
            print(r,r.args)
            cnt+=1
            return get_repo()

if __name__ == '__main__':
    print("start...")
    get_repo()
    csvfile.close()
    print('the end')
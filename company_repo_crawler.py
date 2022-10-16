import time
import csv
import re
import random
from github import Github, RateLimitExceededException, GithubException
from requests import ReadTimeout
from socket import timeout

access_token = "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"

g = Github(login_or_token=access_token,per_page=100)

comp = []

# use regEx to get company name and repos
f = open("jiayun-README.md")
md = f.read()
f.close()
temp = re.findall(r'####.*',md)
for c in temp:
    comp.append(c.replace("#### ",""))

cnt = 0

csvfile1 = open("new/Company_repo"+time.strftime("%Y-%m %H:%M", time.localtime())+".csv","a")
csvfile2 = open("new/Company_commits"+time.strftime("%Y-%m %H:%M", time.localtime())+".csv","a")
w1 = csv.writer(csvfile1)
w2 = csv.writer(csvfile2)
# write the head row
w1.writerow(['organization_name','repo_full_name','URL','contributors_num','description','is_fork','repo_updated_at','repo_firstcommit','repo_lastcommit'])
w2.writerow(['URL','repo_fullname','file','a_specific_commit','its_commit_date','its_event(File.status)','file_firstcommit','file_lastcommit','file_ci_type'])

def company_repo_crawler(current_comp = "", current_repo_id = -1):
    try:
        global g, comp, cnt, w1,w2
        flag_timeout = 0
    
        for c in comp:
            
            if(current_comp != "" and c != current_comp):
                continue        # go to the target company
            else:
                current_comp = ""

            now_comp = c    # defined to return to the function correctly when having exceptions

            org = g.get_organization(c)
            repos = org.get_repos()

            for repo in repos:
                if(current_repo_id != -1 and repo.id != current_repo_id):
                    continue    # go to the target repo
                elif(current_repo_id != -1 and repo.id == current_repo_id):
                    current_repo_id = -1
                    continue

                now_repo_id = repo.id    # defined to return to the function correctly when having exceptions

                cnt+=1
                print('Get repo succefully:'+repo.full_name+','+str(cnt))
                
                # write the csvfile1 first
                # get_commits() return the commit list with the newest commit as the first one
                pg = repo.get_commits()
                firstcommit = pg.reversed[0].commit.author.date
                lastcommit = pg[0].commit.author.date
                org_name = 'NoneType' if(str(type(repo.organization))=="<class \'NoneType\'>") else repo.organization.name

                reco = [org_name,repo.name,repo.url,repo.get_contributors().totalCount,repo.description,repo.fork,repo.updated_at,firstcommit,lastcommit]
                print("writing repos info...")
                w1.writerow(reco)

                # write the csvfile2, use try-and-except block to handle 404 exception if some repos don't use certain CI tool
                try:
                    GHA_yml = set()
                    workflow_commits = repo.get_commits(path="/.github/workflows/")
                    for c in workflow_commits:      # the .totalCount of return value of .get_commits is always 0
                        files = c.files             # so we can't use it to decide whether we get the return value
                        for f in files:             # instead, I just use for wherever it should be the case that totalCount should > 0
                            if(".github/workflows/" in str(f.filename) and ".yml" in str(f.filename)):
                                GHA_yml.add(f.filename)      # get the existed .yml files in GHA path
                    
                    # get commit for every yml file
                    if(len(GHA_yml)>0):
                        for yml in GHA_yml:
                            cmts = repo.get_commits(path=yml)

                            for cm in cmts:                                                 # the .totalCount of return value of .get_commits is always 0
                                file_firstcommit = cmts.reversed[0].commit.author.date      # so we can't use it to decide whether we get the return value
                                file_lastcommit = cmts[0].commit.author.date                # instead, I just use for wherever it should be the case that totalCount should > 0
                                break

                            for cm in cmts:
                                files = cm.files
                                file = None
                                for f in files:
                                    if f.filename == yml:
                                        file = f
                                        break
                                status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                                if(status == "added" or status == "removed"):
                                    w2.writerow([repo.name,yml,cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'GHA'])
                except GithubException as r:
                    print("GHA:"+str(repo.name))
                    print(r)
                finally:
                    GHA_yml.clear()

                try:
                    # get commit for .travis.yml
                    cmts = repo.get_commits(path="/.travis.yml")
                    for cm in cmts:
                        file_firstcommit = cmts.reversed[0].commit.author.date
                        file_lastcommit = cmts[0].commit.author.date
                        break
                    
                    for cm in cmts:
                        files = cm.files
                        file = None
                        for f in files:
                            if f.filename == "/.travis.yml":
                                file = f
                                break
                        status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                        if(status == "added" or status == "removed"):
                            w2.writerow([repo.url,repo.name,"/.travis.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'Travis'])
                except GithubException as r:
                    print("Travis:"+str(repo.name))
                    print(r)

                try:
                    cmts = repo.get_commits(path="/.circleci/config.yml")
                    for cm in cmts:
                        file_firstcommit = cmts.reversed[0].commit.author.date
                        file_lastcommit = cmts[0].commit.author.date
                        break

                    for cm in cmts:
                        files = cm.files
                        file = None
                        for f in files:
                            if f.filename == "/.circleci/config.yml":
                                file = f
                                break
                        status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                        if(status == "added" or status == "removed"):
                            w2.writerow([repo.url,repo.name,"/.circleci/config.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'CircleCI'])
                except GithubException as r:
                    print("CircleCI:"+str(repo.name))
                    print(r)

                try:
                    cmts = repo.get_commits(path="/appveyor.yml")
                    for cm in cmts:
                        file_firstcommit = cmts.reversed[0].commit.author.date
                        file_lastcommit = cmts[0].commit.author.date
                        break

                    for cm in cmts:
                        files = cm.files
                        file = None
                        for f in files:
                            if f.filename == "/appveyor.yml":
                                file = f
                                break
                        status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                        if(status == "added" or status == "removed"):
                            w2.writerow([repo.url,repo.name,"/appveyor.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'AppVeyor'])
                except GithubException as r:
                    print("AppVeyor:"+str(repo.name))
                    print(r)

                try:
                    cmts = repo.get_commits(path="/azure-pipelines.yml")
                    for cm in cmts:
                        file_firstcommit = cmts.reversed[0].commit.author.date
                        file_lastcommit = cmts[0].commit.author.date
                        break

                    for cm in cmts:
                        files = cm.files
                        file = None
                        for f in files:
                            if f.filename == "/azure-pipelines.yml":
                                file = f
                                break
                        status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                        if(status == "added" or status == "removed"):
                            w2.writerow([repo.url,repo.name,"/azure-pipelines.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'Azure'])
                except GithubException as r:
                    print("Azure:"+str(repo.name))
                    print(r)

                try:
                    cmts = repo.get_commits(path="/.gitlab-ci.yml")
                    for cm in cmts:
                        file_firstcommit = cmts.reversed[0].commit.author.date
                        file_lastcommit = cmts[0].commit.author.date
                        break

                    for cm in cmts:
                        files = cm.files
                        file = None
                        for f in files:
                            if f.filename == "/.gitlab-ci.yml":
                                file = f
                                break
                        status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                        if(status == "added" or status == "removed"):
                            w2.writerow([repo.url,repo.name,"/.gitlab-ci.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'GitLab'])
                except GithubException as r:
                    print("GitLab:"+str(repo.name))
                    print(r)

                try:
                    cmts = repo.get_commits(path="/Jenkinsfile")
                    for cm in cmts:
                        file_firstcommit = cmts.reversed[0].commit.author.date
                        file_lastcommit = cmts[0].commit.author.date
                        break

                    for cm in cmts:
                        files = cm.files
                        file = None
                        for f in files:
                            if f.filename == "/Jenkinsfile":
                                file = f
                                break
                        status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                        if(status == "added" or status == "removed"):
                            w2.writerow([repo.url,repo.name,"/Jenkinsfile",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'Jenkins'])
                except GithubException as r:
                    print("Jenkins:"+str(repo.name))
                    print(r)

    except RateLimitExceededException:
        RStime = Github(access_token).rate_limiting_resettime
        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
        stime = RStime-time.time()+0.5
        if stime>0:
            time.sleep(stime)
        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        return company_repo_crawler(now_comp,now_repo_id)
    except (ReadTimeout, timeout) as e:
        flag_timeout+=1
        if flag_timeout==5:
            print("Please check network connection.")
        stime = random.randint(50,70)
        print("Read Timeout... Sleep "+stime+" s.")
        time.sleep(stime)
        print("Try again.")
        flag_timeout -= 1
        return company_repo_crawler(now_comp,now_repo_id)
    except GithubException as r:
        print(r,r.args)
        cnt+=1
        return company_repo_crawler(now_comp,now_repo_id)
        

if __name__ == '__main__':
    print("start...")
    company_repo_crawler()
    csvfile1.close()
    csvfile2.close()
    print('the end')
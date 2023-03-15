import time
import csv
import re
import random
from github import Github, RateLimitExceededException, GithubException
from requests import ReadTimeout
from socket import timeout
from datetime import datetime

access_token = "token"

g = Github(login_or_token=access_token,per_page=100)

comp = ['linkedin', 'facebook', 'google', 'amzn', 'youtube', 'pinterest', 'apple', 'oracle', 'intel', 'IBM', 'vmware', 'Netflix', 'salesforce', 'dell', 'Medium', 'tripadvisor', 'dropbox', 'JetBrains', 'pivotal', 'github', 'redhat-developer', 'square', 'groupon', 'Yelp', 'zynga', 'Juniper']

# use regEx to get company name and repos
# f = open("jiayun-README.md")
# md = f.read()
# f.close()
# temp = re.findall(r'####.*',md)
# for c in temp:
#     comp.append(c.replace("#### ",""))

cnt = 0

csvfile1 = open("res/Repo1_"+time.strftime("%Y-%m %H:%M", time.localtime())+".csv","a")
csvfile2 = open("res/Commits1_"+time.strftime("%Y-%m %H:%M", time.localtime())+".csv","a")
w1 = csv.writer(csvfile1)
w2 = csv.writer(csvfile2)
# write the head row
w1.writerow(['organization_name','repo_id','repo_full_name','URL','total_contributors_num','description','is_fork','repo_updated_at','repo_firstcommit','repo_lastcommit','15_commits','16_commits','17_commits','18_commits','19_commits','20_commits','21_commits','22_commits','15_committer_num','16_committer_num','17_committer_num','18_committer_num','19_committer_num','20_committer_num','21_committer_num','22_committer_num'])
w2.writerow(['URL','repo_id','repo_fullname','file','a_specific_commit','its_commit_date','its_event(File.status)','file_firstcommit','file_lastcommit','file_ci_type'])

now_comp = ""
now_repo_id = -1

def get_year_commmits_and_committer(begin_year, repo):
    end_year = begin_year+1
    begin_dt = datetime(begin_year,1,1)
    end_dt = datetime(end_year,1,1)
    temp = repo.get_commits(since=begin_dt,until=end_dt)
    # get commits num
    commits_count = 0 if(str(type(temp))=="<class \'NoneType\'>") else temp.totalCount
    
    # get committer
    committers = set()
    for i in temp:
        committers.add(i.committer.email)
    committers_num = len(committers)
    return commits_count, committers_num

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

                use_CI = False
                
                now_repo_id = repo.id    # defined to return to the function correctly when having exceptions

                cnt+=1
                print('Get repo succefully:'+repo.full_name+','+str(cnt))
                
                # write the csvfile1 first
                # get_commits() return the commit list with the newest commit as the first one
                pg = repo.get_commits()
                firstcommit = pg.reversed[0].commit.author.date
                lastcommit = pg[0].commit.author.date
                org_name = 'NoneType' if(str(type(repo.organization))=="<class \'NoneType\'>") else repo.organization.name

                # get 2015 to 2022 commits count
                commits_cnt = []
                committer_num = []
                for i in range(2015,2023):
                    cmt, committers=get_year_commmits_and_committer(i,repo)
                    # append commits_count and committer_num into list
                    commits_cnt.append(cmt)
                    committer_num.append(committers)
            
                reco = [org_name,repo.id,repo.name,repo.url,repo.get_contributors().totalCount,repo.description,repo.fork,repo.updated_at,firstcommit,lastcommit]
                reco = reco + commits_cnt + committer_num
                print("writing repos info...")
                w1.writerow(reco)

                # write the csvfile2, use try-and-except block to handle 404 exception if some repos don't use certain CI tool
                while(True):
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
                                    # if(status == "added" or status == "removed" or status == "renamed"):
                                    w2.writerow([repo.url,repo.id,repo.name,yml,cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'GHA'])
                                    use_CI = True
                        # break when successfully ran all the code
                        GHA_yml.clear()
                        break
                    except RateLimitExceededException:
                        # retry
                        GHA_yml.clear()
                        RStime = Github(access_token).rate_limiting_resettime
                        print(str(repo.url)+":"+str(repo.name))
                        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
                        stime = RStime-time.time()+0.5
                        if stime>0:
                            time.sleep(stime)
                        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
                    except GithubException as r:
                        print("EXCEPTION-GHA:"+str(repo.name))
                        print(r)
                        # break when other exceptions occur
                        break
                    except (ReadTimeout, timeout) as e:
                        stime = random.randint(50,70)
                        print("Read Timeout... Sleep "+str(stime)+" s.")
                        time.sleep(stime)
                        print("Try again.")

                # try:
                #     # get commit for .travis.yml
                #     cmts = repo.get_commits(path="/.travis.yml")
                #     for cm in cmts:
                #         file_firstcommit = cmts.reversed[0].commit.author.date
                #         file_lastcommit = cmts[0].commit.author.date
                #         break
                    
                #     for cm in cmts:
                #         files = cm.files
                #         file = None
                #         for f in files:
                #             if f.filename == ".travis.yml":
                #                 file = f
                #                 break
                #         status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                #         if(status == "added" or status == "removed" or status == "renamed"):
                #             w2.writerow([repo.url,repo.name,"/.travis.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'Travis'])
                #             use_CI = True
                # except GithubException as r:
                #     print("Travis:"+str(repo.name))
                #     print(r)

                temp = six_CI_data(repo,"/.travis.yml",".travis.yml",'Travis')
                if(temp):
                    use_CI = temp


                # try:
                #     cmts = repo.get_commits(path="/.circleci/config.yml")
                #     for cm in cmts:
                #         file_firstcommit = cmts.reversed[0].commit.author.date
                #         file_lastcommit = cmts[0].commit.author.date
                #         break

                #     for cm in cmts:
                #         files = cm.files
                #         file = None
                #         for f in files:
                #             if f.filename == ".circleci/config.yml":
                #                 file = f
                #                 break
                #         status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                #         if(status == "added" or status == "removed" or status == "renamed"):
                #             w2.writerow([repo.url,repo.name,"/.circleci/config.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'CircleCI'])
                #             use_CI = True
                # except GithubException as r:
                #     print("CircleCI:"+str(repo.name))
                #     print(r)

                temp = six_CI_data(repo,"/.circleci/config.yml",".circleci/config.yml",'CircleCI')
                if(temp):
                    use_CI = temp

                # try:
                #     cmts = repo.get_commits(path="/appveyor.yml")
                #     for cm in cmts:
                #         file_firstcommit = cmts.reversed[0].commit.author.date
                #         file_lastcommit = cmts[0].commit.author.date
                #         break

                #     for cm in cmts:
                #         files = cm.files
                #         file = None
                #         for f in files:
                #             if f.filename == "appveyor.yml":
                #                 file = f
                #                 break
                #         status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                #         if(status == "added" or status == "removed" or status == "renamed"):
                #             w2.writerow([repo.url,repo.name,"/appveyor.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'AppVeyor'])
                #             use_CI = True
                # except GithubException as r:
                #     print("AppVeyor:"+str(repo.name))
                #     print(r)

                temp = six_CI_data(repo,"/appveyor.yml","appveyor.yml",'AppVeyor')
                if(temp):
                    use_CI = temp


                # try:
                #     cmts = repo.get_commits(path="/azure-pipelines.yml")
                #     for cm in cmts:
                #         file_firstcommit = cmts.reversed[0].commit.author.date
                #         file_lastcommit = cmts[0].commit.author.date
                #         break

                #     for cm in cmts:
                #         files = cm.files
                #         file = None
                #         for f in files:
                #             if f.filename == "azure-pipelines.yml":
                #                 file = f
                #                 break
                #         status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                #         if(status == "added" or status == "removed" or status == "renamed"):
                #             w2.writerow([repo.url,repo.name,"/azure-pipelines.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'Azure'])
                #             use_CI = True
                # except GithubException as r:
                #     print("Azure:"+str(repo.name))
                #     print(r)

                temp = six_CI_data(repo,"/azure-pipelines.yml","azure-pipelines.yml",'Azure')
                if(temp):
                    use_CI = temp

                # try:
                #     cmts = repo.get_commits(path="/.gitlab-ci.yml")
                #     for cm in cmts:
                #         file_firstcommit = cmts.reversed[0].commit.author.date
                #         file_lastcommit = cmts[0].commit.author.date
                #         break

                #     for cm in cmts:
                #         files = cm.files
                #         file = None
                #         for f in files:
                #             if f.filename == ".gitlab-ci.yml":
                #                 file = f
                #                 break
                #         status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                #         if(status == "added" or status == "removed" or status == "renamed"):
                #             w2.writerow([repo.url,repo.name,"/.gitlab-ci.yml",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'GitLab'])
                #             use_CI = True
                # except GithubException as r:
                #     print("GitLab:"+str(repo.name))
                #     print(r)

                temp = six_CI_data(repo,"/.gitlab-ci.yml",".gitlab-ci.yml",'GitLab')
                if(temp):
                    use_CI = temp

                # try:
                #     cmts = repo.get_commits(path="/Jenkinsfile")
                #     for cm in cmts:
                #         file_firstcommit = cmts.reversed[0].commit.author.date
                #         file_lastcommit = cmts[0].commit.author.date
                #         break

                #     for cm in cmts:
                #         files = cm.files
                #         file = None
                #         for f in files:
                #             if f.filename == "Jenkinsfile":
                #                 file = f
                #                 break
                #         status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                #         if(status == "added" or status == "removed" or status == "renamed"):
                #             w2.writerow([repo.url,repo.name,"/Jenkinsfile",cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'Jenkins'])
                #             use_CI = True
                # except GithubException as r:
                #     print("GitLab:"+str(repo.name))
                #     print(r)

                
                temp = six_CI_data(repo,"/Jenkinsfile","Jenkinsfile",'Jenkins')
                if(temp):
                    use_CI = temp
                
                # write no-CI-using-history repo's info in commits.csv 
                if(use_CI == False):
                    w2.writerow([repo.url,repo.id,repo.name,"NULL","NULL","NULL","NULL","NULL","NULL","NULL"])

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
        print("Read Timeout... Sleep "+str(stime)+" s.")
        time.sleep(stime)
        print("Try again.")
        flag_timeout -= 1
        return company_repo_crawler(now_comp,now_repo_id)
    except GithubException as r:
        print(r,r.args)
        cnt+=1
        return company_repo_crawler(now_comp,now_repo_id)

def six_CI_data(repo,path,filename,CI):
    global w2,access_token
    while(True):
        try:
            use_CI = False
            cmts = repo.get_commits(path=path)
            for cm in cmts:
                file_firstcommit = cmts.reversed[0].commit.author.date
                file_lastcommit = cmts[0].commit.author.date
                break

            for cm in cmts:
                files = cm.files
                file = None
                for f in files:
                    if f.filename == filename:
                        file = f
                        break
                status = 'NoneType' if(str(type(file))=="<class \'NoneType\'>") else file.status
                # if(status == "added" or status == "removed" or status == "renamed"):
                w2.writerow([repo.url,repo.id,repo.name,path,cm.sha,cm.commit.author.date,status,file_firstcommit,file_lastcommit,CI])
                use_CI = True
            
            return use_CI
        except RateLimitExceededException:
            RStime = Github(access_token).rate_limiting_resettime
            print(str(repo.url)+":"+str(repo.name))
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        except GithubException as r:
            print("EXCEPTION-"+str(CI)+':'+str(repo.name))
            print(r)
            # return None when other exceptions occur
            return None
        except (ReadTimeout, timeout) as e:
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
        

if __name__ == '__main__':
    print("start...")
    company_repo_crawler()
    csvfile1.close()
    csvfile2.close()
    print('the end')
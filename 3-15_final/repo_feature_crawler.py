import time
import json
import random
import traceback
import os
from github import Github, RateLimitExceededException, GithubException
from requests import ReadTimeout, Timeout
from socket import timeout
from datetime import datetime
from urllib3.exceptions import MaxRetryError
from utils import mkdir, json_serial, skip_status, too_large


access_token = "token"
flag_timeout = 0
cnt = 0
target_repo = None


def my_totalCount(obj):
    global access_token, flag_timeout
    while(True):
        try:
            return obj.totalCount
        except GithubException as r:
            msg = traceback.format_exc()
            for status in skip_status:
                if status in msg:
                    print("[my_totalCount]:Skipped")
                    return 0		
            if too_large in msg:
                print("[my_totalCount]:Too large")
                return -1		
        except RateLimitExceededException:
            RStime = Github(access_token).rate_limiting_resettime
            print("[my_totalCount]: Rate limit exception.")
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        except (ReadTimeout, timeout, Timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
                # print(traceback.format_exc())
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1


def get_obj_by_func(func, **params):
    global access_token, flag_timeout
    while(True):
        try:
            temp = func(**params)
            return temp
        except RateLimitExceededException:
            # retry
            RStime = Github(access_token).rate_limiting_resettime
            print("[get_obj_by_func]: Rate limit exception.")
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        except GithubException as r:
            msg = traceback.format_exc()
            for status in skip_status:
                if status in msg:
                    # empty Exception, skip this repo
                    print("[get_obj_by_func]:Skip, "+str(func)+str(r))
                    # print(traceback.format_exc())
                    return None
            print("get_obj_by_func:" + str(func)+" GHE, Try again. "+str(r))
            time.sleep(1)
        except (ReadTimeout, timeout, Timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
                # print(traceback.format_exc())
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1


def get_year_commmits_and_committer(begin_year, repo):
    end_year = begin_year+1
    begin_dt = datetime(begin_year,1,1)
    end_dt = datetime(end_year,1,1)

    temp = get_obj_by_func(repo.get_commits,since=begin_dt,until=end_dt)
    committers = set()
    if("NoneType" in str(type(temp))):
    # get commits num
        commits_count = 0  
    else:
        commits_count = my_totalCount(temp)
        # get committer
        for i in temp:
            try:
                if("NoneType" not in str(type(i.author))):
                    committers.add(i.author.id)
            except GithubException as e:
                print("committers.add(i.author.id):"+str(e))
    committers_num = len(committers)
    return commits_count, committers_num


def six_CI_data(repo,path,filename,CI):
    global access_token, flag_timeout
    vice_title = ['file_name','commit_date','status','first_commit','last_commit','CI_type','sha']
    result = []
    
    cmts = get_obj_by_func(repo.get_commits,path=path)
    if("NoneType" not in str(type(cmts))):
        try:
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
                status = None if("NoneType" in str(type(file))) else file.status
                # if(status == "added" or status == "removed" or status == "renamed"):
                reco = [path,cm.commit.author.date,status,file_firstcommit,file_lastcommit,CI,cm.sha]
                result.append(dict(zip(vice_title,reco)))
            return {CI:result}
        except GithubException as e:
            print("[For cm in cmts " + CI +" ]:"+str(e))
            return {CI:dict(zip(vice_title,[]))}
        except (ReadTimeout, timeout, Timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
                # print(traceback.format_exc())
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1

    else:
        return {CI:dict(zip(vice_title,[]))}


def get_API_features(repo, writer):
    global flag_timeout
    """
        features: 
            id
            name
            full_name
            organization.name
            organization.id
            created_at
            pushed_at
            updated_at
            fork (bool)
            forks
            forks_count
            has_downloads
            has_issues
            has_pages
            has_projects
            has_wiki
            homepage (trans to bool?)
            language
            open_issues
            open_issues_count
            size (judge if the repo is empty)
            stargazers_count
            subscribers_count
            watchers
            watchers_count
            first_commit (through my function)
            last_commit (through my function)
            get_branches() totalCount
            # get_collaborators() totalCount : no permission
            get_comments() totalCount
            get_commits() totalCount
            get_contributors() totalCount
            get_downloads() totalCount
            get_events() totalCount
            get_issues() totalCount
            get_labels() totalCount
            get_milestones() totalCount
            get_pulls() totalCount,open PR count
            get_readme() (get its size)
            get_releases() totalCount
            get_topics() totalCount
            commit_count (per year, use my function)
            contributor_count  (per year, use my function)
    """

    feature_title = ['id','name','full_name','org_name','org_id','created_at','pushed_at','updated_at',
                    'isFork','forks','forks_count','has_downloads','has_issues','has_pages','has_projects',
                    'has_wiki','homepage','language','open_issues','open_issues_count','size',
                    'stargazers_count','subscribers_count','watchers','watchers_count','first_commit',
                    'last_commit','branches_count','commit_comments_count',
                    'commits_count','countributors_count','downloads_count','events_count','issues_count',
                    'labels_count','milestones_count','PR_count','open_PR_count','readme_size','release_count',
                    'topic_count','15_commits','16_commits','17_commits','18_commits','19_commits',
                    '20_commits','21_commits','22_commits','15_committer_num','16_committer_num','17_committer_num',
                    '18_committer_num','19_committer_num','20_committer_num','21_committer_num','22_committer_num']

    # get_commits() return the commit list with the newest commit as the first one
    
    pg = get_obj_by_func(repo.get_commits)
    if("NoneType" in str(type(pg))):
        return False

    firstcommit = "NULL"
    lastcommit = "NULL"
    org_name = None
    org_id = None

    try_flag = True
    while(try_flag):
        try:
            org_name = None if("NoneType" in str(type(repo.organization))) else repo.organization.name
            org_id = None if("NoneType" in str(type(repo.organization))) else repo.organization.id
            break
        except RateLimitExceededException:
            RStime = Github(access_token).rate_limiting_resettime
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        except GithubException as r:
            msg = traceback.format_exc()
            for status in skip_status:
                if status in msg:
                    # empty Exception, skip this repo
                    print("[org_name] skip:" + str(r))
                    try_flag = False
                    break
            if(try_flag):
                print("[org_name] : GHE, Try again. "+str(r))
                time.sleep(1)                
        except (ReadTimeout, timeout, Timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
                # print(traceback.format_exc())
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1

    # get 2015 to 2022 commits count
    commits_cnt = []
    committer_num = []
    firstcommit = None
    lastcommit = None

    try_flag = True
    while(try_flag):
        try:
            firstcommit = pg.reversed[0].commit.author.date
            lastcommit = pg[0].commit.author.date
            for i in range(2015,2023):
                cmt, committers = get_year_commmits_and_committer(i,repo)
                # append commits_count and committer_num into list
                commits_cnt.append(cmt)
                committer_num.append(committers)
            break
        except RateLimitExceededException:
            # retry
            RStime = Github(access_token).rate_limiting_resettime
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        except GithubException as r:
            msg = traceback.format_exc()
            for status in skip_status:
                if status in msg:
                    # empty Exception, skip this repo
                    print("EXCEPTION-COMMITTER:skip, "+str(r))
                    try_flag = False
                    break
            if(try_flag):
                print("[EXCEPTION-COMMITTER:] GHE, Try again. "+str(r))
                time.sleep(1)
        except (ReadTimeout, timeout, Timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
                # print(traceback.format_exc())
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1

    try_flag = True
    while(try_flag):
        try:
            reco = [repo.id,repo.name,repo.full_name,org_name,org_id,repo.created_at,repo.pushed_at,repo.updated_at,
                    repo.fork,repo.forks,repo.forks_count,repo.has_downloads,repo.has_issues,repo.has_pages,repo.has_projects,
                    repo.has_wiki,repo.homepage,repo.language,repo.open_issues,repo.open_issues_count,repo.size,repo.stargazers_count,
                    repo.subscribers_count,repo.watchers,repo.watchers_count,firstcommit,lastcommit]
            break
        except RateLimitExceededException:
            # retry
            RStime = Github(access_token).rate_limiting_resettime
            print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
            stime = RStime-time.time()+0.5
            if stime>0:
                time.sleep(stime)
            print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        except GithubException as r:
            msg = traceback.format_exc()
            for status in skip_status:
                if status in msg:
                    # empty Exception, skip this repo
                    print("reco: skip, "+str(r))
                    try_flag = False
                    reco = []
                    break
            if(try_flag):
                print("[reco]: GHE, Try again. "+str(r))
                time.sleep(1)
        except (ReadTimeout, timeout, Timeout) as e:
            flag_timeout+=1
            if flag_timeout==5:
                print("Please check network connection.")
                # print(traceback.format_exc())
            stime = random.randint(50,70)
            print("Read Timeout... Sleep "+str(stime)+" s.")
            time.sleep(stime)
            print("Try again.")
            flag_timeout -= 1


    temp = get_obj_by_func(repo.get_branches)
    branches_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_comments)       
    commit_comments_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)
    
    temp = get_obj_by_func(repo.get_commits)
    commits_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_contributors)
    countributors_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_downloads)
    downloads_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_events)
    events_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_issues)
    issues_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_labels)
    labels_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_milestones)
    milestones_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_pulls,state="all")
    PR_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_pulls,state="open")
    open_PR_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)

    temp = get_obj_by_func(repo.get_readme)
    readme_size = 0 if("NoneType" in str(type(temp))) else temp.size
    
    temp = get_obj_by_func(repo.get_releases)
    release_count = 0 if("NoneType" in str(type(temp))) else my_totalCount(temp)
    
    temp = get_obj_by_func(repo.get_topics)
    topic_count = 0 if("NoneType" in str(type(temp))) else len(temp)
    
    reco.extend([branches_count,commit_comments_count,commits_count,countributors_count,downloads_count,
                    events_count,issues_count,labels_count,milestones_count,PR_count,open_PR_count,readme_size,release_count,topic_count])

    reco = reco + commits_cnt + committer_num
    jsonObj = json.dumps(dict(zip(feature_title,reco)),indent=4, default=json_serial, separators=(',', ': '), ensure_ascii=False)
    writer.write(jsonObj)
    return True


def get_stargazer(repo, writer, notEmpty):
    """
        feature:
            get_stargazers_with_dates() (stargazer_timestamp)
    """
    global flag_timeout
    if(notEmpty):
        feature_title = ['stargazer_date']
        sdate = get_obj_by_func(repo.get_stargazers_with_dates)
        stargazers = {}

        if("NoneType" not in str(type(sdate))):
            try:
                for s in sdate:
                    try:
                        stargazers[s.user.id] = s.starred_at		
                    except RateLimitExceededException:
                        RStime = Github(access_token).rate_limiting_resettime
                        print("Rate limit exception.")
                        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
                        stime = RStime-time.time()+0.5
                        if stime>0:
                            time.sleep(stime)
                        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
                    except (ReadTimeout, timeout, Timeout) as e:
                        flag_timeout+=1
                        if flag_timeout==5:
                            print("Please check network connection.")
                            # print(traceback.format_exc())
                        stime = random.randint(50,70)
                        print("Read Timeout... Sleep "+str(stime)+" s.")
                        time.sleep(stime)
                        print("Try again.")
                        flag_timeout -= 1
                    except GithubException as r:
                        print("[stargazer]:" + str(r))
            except RateLimitExceededException:
                        RStime = Github(access_token).rate_limiting_resettime
                        print("Rate limit exception.")
                        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
                        stime = RStime-time.time()+0.5
                        if stime>0:
                            time.sleep(stime)
                        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))

        reco = [stargazers]
        jsonObj = json.dumps(dict(zip(feature_title,reco)),indent=4, default=json_serial, separators=(',', ': '), ensure_ascii=False)
    else:
        jsonObj = json.dumps(dict(zip(feature_title,[])),indent=4, default=json_serial, separators=(',', ': '), ensure_ascii=False)
    writer.write(jsonObj)


def get_CI_file_commits(repo, writer, notEmpty):
    global flag_timeout
    """
        feature:
            CI_file_commits (filename, commit_date, event, first, last, CI_type, use my function)
    """
    feature_title = ['CI_file_commits']
    vice_title = ['file_name','commit_date','status','first_commit','last_commit','CI_type','sha']
    all_CI = []

    if(notEmpty):
        # use try-and-except block to handle 404 exception if some repos don't use certain CI tool
        try_flag = True
        while(try_flag):
            try:
                GHA_yml = set()
                workflow_commits = get_obj_by_func(repo.get_commits,path="/.github/workflows/")
                if("NoneType" not in str(type(workflow_commits))):
                    for c in workflow_commits:      # the .totalCount of return value of .get_commits is always 0
                        files = c.files             # so we can't use it to decide whether we get the return value
                        for f in files:             # instead, I just use for wherever it should be the case that totalCount should > 0
                            if(".github/workflows/" in str(f.filename) and ".yml" in str(f.filename)):
                                GHA_yml.add(f.filename)      # get the existed .yml files in GHA path
                
                # get commit for every yml file
                if(len(GHA_yml)>0):
                    result = []
                    for yml in GHA_yml:
                        cmts = get_obj_by_func(repo.get_commits,path=yml)

                        if("NoneType" not in str(type(cmts))):
                            try:
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
                                    status = None if("NoneType" in str(type(file))) else file.status
                                    # if(status == "added" or status == "removed" or status == "renamed"):
                                    reco = [yml,cm.commit.author.date,status,file_firstcommit,file_lastcommit,'GHA',cm.sha]
                                    result.append(dict(zip(vice_title,reco)))
                            except RateLimitExceededException:
                                # retry
                                RStime = Github(access_token).rate_limiting_resettime
                                print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
                                stime = RStime-time.time()+0.5
                                if stime>0:
                                    time.sleep(stime)
                                print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
                            except GithubException as e:
                                print("[GHA cm in cmts]:"+str(e))
                    all_CI.append({"GHA":result})
                else:
                    all_CI.append({"GHA":dict(zip(vice_title,[]))})
                # break when successfully ran all the code
                GHA_yml.clear()
                break
            except RateLimitExceededException:
                # retry
                GHA_yml.clear()
                RStime = Github(access_token).rate_limiting_resettime
                print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
                stime = RStime-time.time()+0.5
                if stime>0:
                    time.sleep(stime)
                print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
            except GithubException as r:
                print("[CI file commits] EXCEPTION-GHA:"+str(repo.name))
                msg = traceback.format_exc()
                for status in skip_status:
                    if status in msg:
                        # empty Exception, skip this repo
                        print("EXCEPTION-GHA:skip, "+str(r))
                        all_CI.append({"GHA":dict(zip(vice_title,[]))})
                        try_flag = False
                        break
                if(try_flag):
                    print("Try again."+str(r))
                    time.sleep(1)    
            except (ReadTimeout, timeout, Timeout) as e:
                flag_timeout+=1
                if flag_timeout==5:
                    print("Please check network connection.")
                    # print(traceback.format_exc())
                stime = random.randint(50,70)
                print("Read Timeout... Sleep "+str(stime)+" s.")
                time.sleep(stime)
                print("Try again.")
                flag_timeout -= 1

        tempDict = six_CI_data(repo,"/.travis.yml",".travis.yml",'Travis')
        all_CI.append(tempDict)

        tempDict = six_CI_data(repo,"/.circleci/config.yml",".circleci/config.yml",'CircleCI')
        all_CI.append(tempDict)

        tempDict = six_CI_data(repo,"/appveyor.yml","appveyor.yml",'AppVeyor')
        all_CI.append(tempDict)

        tempDict = six_CI_data(repo,"/azure-pipelines.yml","azure-pipelines.yml",'Azure')
        all_CI.append(tempDict)

        tempDict = six_CI_data(repo,"/.gitlab-ci.yml",".gitlab-ci.yml",'GitLab')
        all_CI.append(tempDict)
        
        tempDict = six_CI_data(repo,"/Jenkinsfile","Jenkinsfile",'Jenkins')
        all_CI.append(tempDict)
    
    else: 
        CI_list = ['GHA','Travis','CircleCI','AppVeyor','Azure','GitLab','Jenkins']
        for ci in CI_list:
            all_CI.append({ci:dict(zip(vice_title,[]))})

    jsonObj = json.dumps(all_CI,indent=4, default=json_serial, separators=(',', ': '), ensure_ascii=False)
    writer.write(jsonObj)


def get_repo_feature(repo, comp, dirname = None):
    """
        Get a single repo's feeature, will create according new json file.
    """
    global cnt, flag_timeout
    cnt+=1
    notEmpty = True
    print('Get repo successfully:'+repo.full_name+','+str(repo.id)+','+str(cnt))
    if("NoneType" in str(type(dirname))):
        file_path = "res/" + comp.name.replace(" ","_") + "/" + str(repo.id)+".json"
    else:
        file_path = "res/" + dirname + "/" + str(repo.id)+".json"
    if(os.path.exists(file_path)):
        # already crawled this repo
        print("Already crawled.")
    else:
        repo_json_file = open(file_path,"w")
        notEmpty = get_API_features(repo, repo_json_file)
        get_stargazer(repo,repo_json_file,notEmpty)
        get_CI_file_commits(repo,repo_json_file,notEmpty)
        if(not notEmpty):
            print("[Repo " + repo.name +" is empty.]")
        repo_json_file.close()


def get_org_feature(org, dirname = None, org_writer = None):
    """
        Get a single orgnization's feature, will store all orgnizations' features into one JSON file.
        ** Please run organization_feature-crawler.py to crawl organizations' feature.
    """
    global target_repo
    repos = get_obj_by_func(org.get_repos)
    
    if("NoneType" not in str(type(repos))):
        # for each repo in the org, get repo features:
        for repo in repos:
            if("NoneType" not in str(type(target_repo))):
                # need to skip some repos
                if(repo.id < target_repo):
                    continue
                else:
                    target_repo = None
                    get_repo_feature(repo,org, dirname = dirname)
            else:
                get_repo_feature(repo,org, dirname = dirname)
    

def start_crawler(comp, token, target = None):
    print("start...")
    # change the token been used
    global access_token, target_repo
    access_token = token
    target_repo = target
    g = Github(login_or_token=access_token,per_page=100)
    for c in comp:
        dirname = c.replace(" ","_")
        org = get_obj_by_func(g.get_organization,login=c)
        mkdir("res/"+c.replace(" ","_"))
        
        try:
            get_org_feature(org,dirname = dirname)
        except ConnectionResetError as r:
            print("ConnectionResetError")
            # print(traceback.format_exc())
            time.sleep(10)
            get_org_feature(org,dirname = dirname)
        except MaxRetryError as r:
            print("MaxRetryError")
            # print(traceback.format_exc())
            time.sleep(10)
            get_org_feature(org,dirname = dirname)
    print('the end')
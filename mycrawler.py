from sys import maxsize
import time
import csv
from github import Github, RateLimitExceededException, Organization


access_token = "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"

g = Github(login_or_token=access_token,per_page=100)

csvfile = open("/Users/andyluo/Desktop/Test1_"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+".csv","a")
w = csv.writer(csvfile)
# write the head row
w.writerow(['repo_full_name','id','URL','stars','allow_merge_commit','allow_rebase_merge',
'allow_squash_merge','archived','archive_url','assignees_url','blobs_url','branches_url','clone_url','collaborators_url',
'comments_url','commits_url','compare_url','contents_url','contributors_url','created_at','default_branch','delete_branch_on_merge',
'deployments_url','description','downloads_url','events_url','fork','forks','forks_count','forks_url','git_commits_url','git_refs_url',
'git_tags_url','git_url','has_downloads','has_issues','has_pages','has_projects','has_wiki','homepage','hooks_url','html_url','issue_comment_url',
'issue_events_url','issues_url','keys_url','labels_url','language','languages_url','master_branch','merges_url','milestones_url','mirror_url',
'network_count','notifications_url','open_issues','open_issues_count','organization_name','owner_name','parent_name','parent_url','permissions_admin',
'permissions_maintain','permissions_pull','permissions_push','permissions_triage','private','pulls_url','pushed_at',
'releases_url','size','source_name','source_url','ssh_url','stargazers_url','statuses_url','subscribers_url','subscribers_count','subscription_url','svn_url','tags_url',
'teams_url','trees_url','updated_at','watchers','watchers_count'])

def get_repos(token,stars,round):
    global g,w
    try:
        # get top 10,000 popular repos  
        while round < 10:
            q = "stars:1.."+str(stars)
            repos = g.search_repositories(query=q,sort="stars",order="desc")

            for repo in repos:
                #write repo's attribute
                stars = repo.stargazers_count

                org_name = 'NoneType' if(str(type(repo.organization))=="<class \'NoneType\'>") else repo.organization.name
                owner_name = 'NoneType' if(str(type(repo.owner))=="<class \'NoneType\'>") else repo.owner.name
                parent_name = 'NoneType' if(str(type(repo.parent))=="<class \'NoneType\'>") else repo.parent.name
                parent_url = 'NoneType' if(str(type(repo.parent))=="<class \'NoneType\'>") else repo.parent.url
                source_name = 'NoneType' if(str(type(repo.source))=="<class \'NoneType\'>") else repo.source.name
                source_url = 'NoneType' if(str(type(repo.source))=="<class \'NoneType\'>") else repo.source.url

                reco = [repo.name,repo.id,repo.url,repo.stargazers_count,repo.allow_merge_commit,repo.allow_rebase_merge,
                repo.allow_squash_merge,repo.archived,repo.archive_url,repo.assignees_url,repo.blobs_url,repo.branches_url,repo.clone_url,repo.collaborators_url,
                repo.comments_url,repo.commits_url,repo.compare_url,repo.contents_url,repo.contributors_url,repo.created_at,repo.default_branch,repo.delete_branch_on_merge,
                repo.deployments_url,repo.description,repo.downloads_url,repo.events_url,repo.fork,repo.forks,repo.forks_count,repo.forks_url,repo.git_commits_url,repo.git_refs_url,
                repo.git_tags_url,repo.git_url,repo.has_downloads,repo.has_issues,repo.has_pages,repo.has_projects,repo.has_wiki,repo.homepage,repo.hooks_url,repo.html_url,repo.issue_comment_url,
                repo.issue_events_url,repo.issues_url,repo.keys_url,repo.labels_url,repo.language,repo.languages_url,repo.master_branch,repo.merges_url,repo.milestones_url,repo.mirror_url,
                repo.network_count,repo.notifications_url,repo.open_issues,repo.open_issues_count,org_name,owner_name,parent_name,parent_url,repo.permissions.admin,repo.permissions.maintain,
                repo.permissions.pull,repo.permissions.push,repo.permissions.triage,repo.private,repo.pulls_url,repo.pushed_at,
                repo.releases_url,repo.size,source_name,source_url,repo.ssh_url,repo.stargazers_url,repo.statuses_url,repo.subscribers_url,repo.subscribers_count,repo.subscription_url,repo.svn_url,repo.tags_url,
                repo.teams_url,repo.trees_url,repo.updated_at,repo.watchers,repo.watchers_count]
                w.writerow(reco)
            w.writerow(['#','#','#']) 
            print(g.get_rate_limit().search)
            print("now round:"+str(round))
            round += 1
            time.sleep(60)
        
    except RateLimitExceededException:
        RStime = Github(token).rate_limiting_resettime
        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
        print("limiting:"+str(g.rate_limiting))
        print("search"+str(g.get_rate_limit().search))
        stime = 10
        if stime>0:
            time.sleep(stime)
        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        w.writerow(['!!!','!!!','!!!']) 
        return get_repos(token,stars,round)

if __name__ == '__main__':
    max_star = 300000
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
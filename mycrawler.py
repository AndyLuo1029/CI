import time
import csv
from tkinter import W
from github import Github, RateLimitExceededException


access_token = "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"

g = Github(login_or_token=access_token,per_page=100)

csvfile = open("/Users/andyluo/Desktop/"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+".csv","a")
w = csv.writer(csvfile)
# write the head row
w.writerow(['repo_name','URL','stars'])

def get_repos(token,stars):
    global g,w
    try:
        # get top 10,000 popular repos  
        for i in range(0,10):
            q = "stars:<="+str(stars)
            repos = g.search_repositories(query=q,sort="stars",order="desc")

            for repo in repos:
                #write repo's attribute
                stars = repo.stargazers_count
                reco = [repo.full_name, repo.url, repo.stargazers_count]
                w.writerow(reco)
            w.writerow(['#','#','#']) 
            print(g.get_rate_limit().search)
        
    except RateLimitExceededException:
        RStime = Github(token).rate_limiting_resettime
        print(time.strftime("[%H:%M]", time.localtime()),time.strftime("API rate limit exceeded. Reset at %x %X",time.localtime(RStime)))
        print("limiting:"+str(g.rate_limiting))
        print("search"+str(g.get_rate_limit().search))
        stime = 60
        if stime>0:
            time.sleep(stime)
        print(time.strftime("[%H:%M] Get back to work!", time.localtime()))
        w.writerow(['!!!','!!!','!!!']) 
        return get_repos(token,stars)

if __name__ == '__main__':
    get_repos(access_token,300000)
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
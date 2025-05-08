import json as j
import requests as rq
from github import *
import os



GITHUB_TOKEN = os.getenv('githubtk')
REPO = "junkyard"


class DB:
    def __init__(self,token=GITHUB_TOKEN,author=("sortalost",".."),reponame=f"sortalost/{REPO}", main="main.json"):
        self.token=token
        self.branch=branch
        self.author=InputGitAuthor("sortalost",str(os.getenv('email')))
        self.github=Github(self.token)
        self.repo=self.github.get_repo(reponame)
        self.main=main


    def get_remote_data(self,path=None):
        path=path or self.main
        con = self.repo.get_contents(path,ref=self.branch).decoded_content.decode("utf-8")
        return eval(con)


    def push_remote_data(self,content,path=None,msg="Raw API"):
        path=path or self.main
        try:
            self.repo.create_file(path,msg,str(content),branch=self.branch)
        except:
            sha = self.repo.get_contents(path,ref=self.branch).sha
            self.repo.update_file(path,msg,str(content),sha,branch=self.branch)
        return content

    def to_file(self,con,fp=None,json=True,mode="w"):
        fp=fp or self.main
        with open(fp,mode) as f:
            if json is True:
                j.dump(con,f,indent=4)
            else:
                f.write(con)
        return con

    def sync(self,fp=None,prefer="cloud",dry=False):
        prefer=prefer.lower()
        fp=fp or self.main
        dry=bool(dry)
        allowed=['cloud','local','api']
        if prefer not in allowed:
            raise TypeError(f"Args must be {', '.join(allowed)}; not {prefer}!!")
        if dry is True:
            return load_file(fp)==gb.get_remote_data(fp)==gb.get_remote_data(fp,api=1)
        if prefer=="cloud":
            self.to_file(self.get_remote_data(fp),fp)
            self.push_remote_data(self.get_remote_data(fp),api=1)
            return load_file(fp)==self.get_remote_data(fp)==self.get_remote_data(fp,api=1), "Overrided API data and LOCAL data"

        elif prefer=="api":
            if load_file(fp)==self.get_remote_data(fp)==self.get_remote_data(fp,api=1):
                return True,"Already Synced!!"
            self.to_file(self.get_remote_data(fp,api=True))
            self.push_remote_data(self.get_remote_data(fp,api=True))
            return load_file(fp)==self.get_remote_data(fp)==self.get_remote_data(fp,api=1), "Overrided CLOUD data and LOCAL data"

        elif prefer=="local":
            if load_file(fp)==self.get_remote_data(fp)==self.get_remote_data(fp,api=1):
                return True,"Already Synced!!"
            self.push_remote_data(load_file(fp))
            self.push_remote_data(self.get_remote_data(),api=1)
            return load_file(fp)==self.get_remote_data(fp)==self.get_remote_data(fp,api=1), "Overrided API data and CLOUD data"
 
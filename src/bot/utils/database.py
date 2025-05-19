import json as j
import requests as rq
from github import *
import os



GITHUB_TOKEN = os.getenv('GITHUBTK')
REPO = "junkyard"


class DB:
    def __init__(self,token=GITHUB_TOKEN, branch="master",author=("sortalost",".."),reponame=f"sortalost/{REPO}", main="main.json"):
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

    def sync(self,fp=None):
        fp=fp or self.main
        
        self.to_file(self.get_remote_data(fp),fp)
        
'''
 /$$      /$$                       /$$               /$$      
| $$$    /$$$                      | $$              | $$      
| $$$$  /$$$$  /$$$$$$   /$$$$$$  /$$$$$$   /$$$$$$$ | $$$$$$$ 
| $$ $$/$$ $$ |____  $$ /$$__  $$|_  $$_/  | $$__  $$| $$__  $$
| $$  $$$| $$  /$$$$$$$| $$  \ $$  | $$    | $$  \ $$| $$  \ $$
| $$\  $ | $$ /$$__  $$| $$  | $$  | $$ /$$| $$  | $$| $$  | $$
| $$ \/  | $$|  $$$$$$$| $$$$$$$/  |  $$$$/| $$  | $$| $$  | $$
|__/     |__/ \_______/| $$____/    \___/  |__/  |__/|__/  |__/
                       | $$                                    
                       | $$                                    
                       |__/                                    '''
import requests
from time import sleep
from datetime import date
from tqdm import tqdm
import json
import csv

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": ""    
}


class github_repos:
    def __init__(self, page: int = 0, proxy_ip: str = None, proxy_port: int = None):
        self.page = page
        self.proxy = {'http': f'http://{proxy_ip}:{proxy_port}', 'https': f'http://{proxy_ip}:{proxy_port}'} if proxy_ip else None
        self.json_file = 'resource/repos.json'
        self.csv_file = 'resource/repos.csv'

    def run(self):
        if self.__test_github_com():
            data = self.__fetch_new_repos(self.page)
            self.__save_file(data)
 
    def __test_github_com(self):
        res = requests.get("https://api.github.com", headers=headers, proxies=self.proxy)
        if res.status_code == 200:
            print("[+] GitHub.com is reachable")
            return True
        else:
            print("[-] GitHub.com is not reachable")
            return False
        
    def __fetch_new_repos(self, max_pages:int):
        repos_ = {}
        repos = []
        base_url = "https://api.github.com/search/repositories"
        progress = tqdm(range(1, max_pages + 1), desc="[UPDATE]", unit="Mb")
        for page in progress:
            params = {
                "q": "created:>={}".format(date.today().strftime("%Y-%m-%d")),
                "sort": "created",
                "order": "desc",
                "per_page": 100,
                "page": page
            }
            r = requests.get(base_url, headers=headers, params=params, proxies=self.proxy)
            if r.status_code != 200:
                print(f"Error: {r.status_code} - {r.text}")
                break
            data = r.json()
            items = data.get("items", [])
            repos.append(items)
            sleep(1)
        repos_['data'] = repos
        return repos_

    def __save_file(self, data:dict):
        fieldnames = ['full_name', 'stargazers_count', 'html_url', 'forks_count', 'language', 'description']
        with open(self.json_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
            
        print("[UPDATE] Update completed.")
        
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for layer1 in data['data']:
                for repo in layer1:
                    row = {k: repo.get(k, '') for k in fieldnames}
                    writer.writerow(row)

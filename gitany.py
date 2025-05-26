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
import json
import csv
import os
import re
import matplotlib.pyplot as plt
from collections import Counter
from lib import github as gitrepo

LOGO = r'''
        .__  __                       
   ____ |__|/  |______    ____ ___.__.
  / ___\|  \   __\__  \  /    <   |  |
 / /_/  >  ||  |  / __ \|   |  \___  |
 \___  /|__||__| (____  /___|  / ____|
/_____/               \/     \/\/     
Maptnh@S-H4CK13         gitany version 1.0
       https://github.com/MartinxMax
'''

class GitAny:
    def __init__(self):
        self.json_path = "./resource/repos.json"
        self.csv_path = "./resource/repos.csv"
        self.commands = {
            'search': self.search_command,
            'graphy': self.graphy,
            'help': self.show_help,
            'update': self.update_data,
            'exit': self.exit_cli
        }

    def run(self):
        print("[*] GitAny CLI started. Type 'help' for commands.")
        while True:
            try:
                command = input("gitany$ ").strip()
                if not command:
                    continue
                cmd_name, *args = command.split()
                if cmd_name in self.commands:
                    self.commands[cmd_name](" ".join(args))
                else:
                    print(f"[ERROR] Unknown command: {cmd_name}")
            except KeyboardInterrupt:
                print("\n[!] Interrupted by user. Exiting.")
                break

    def show_help(self, _=None):
        print("""
[GitAny Command Help]
    search dec=<keyword>        Search by description (fuzzy)
    search lan=<keyword>        Search by language (fuzzy)
    search repo=<keyword>       Search by repository full_name (fuzzy)
    search star<>=500           Search by stargazers_count (supports > >= < <= =)
    search fork<=1000           Search by forks_count (supports > >= < <= =)
    search all                  Show all repositories
    graphy                      Visualize CSV data with Matplotlib
    update                      Update repository data
    help                        Show this help message
    exit                        Exit GitAny CLI
""")

    def search_command(self, args):
        if args == "all":
            self.search_all()
        elif args.startswith("dec="):
            keyword = args[4:].lower()
            self.search_json("description", keyword)
        elif args.startswith("lan="):
            keyword = args[4:].lower()
            self.search_json("language", keyword)
        elif args.startswith("repo="):
            keyword = args[5:].lower()
            self.search_json("full_name", keyword)
        elif args.startswith("star") or args.startswith("fork"):
            self.search_numeric(args)
        else:
            print("[ERROR] Invalid search syntax. Use 'help' to see commands.")
    def search_all(self):
        if not os.path.exists(self.json_path):
            print(f"[ERROR] JSON file not found: {self.json_path}")
            return
        with open(self.json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)['data']
            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                return

        print("[SEARCH] Showing all repositories:")
        for layer in data:
            for repo in layer:
                self.print_repo(repo)

    def search_json(self, field, keyword):
        if not os.path.exists(self.json_path):
            print(f"[ERROR] JSON file not found: {self.json_path}")
            return
        with open(self.json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)['data']
            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                return

        print(f"[SEARCH] Searching for '{keyword}' in field '{field}':")
        for layer in data:
            for repo in layer:
                value = repo.get(field, "")
                if value and keyword in str(value).lower():
                    self.print_repo(repo)

    def search_numeric(self, expr):
        if not os.path.exists(self.json_path):
            print(f"[ERROR] JSON file not found: {self.json_path}")
            return

        match = re.match(r'(star|fork)\s*(<=|>=|=|<|>)\s*(\d+)', expr)
        if not match:
            print("[ERROR] Invalid numeric search format. Use: search star>=1000")
            return

        field_map = {
            'star': 'stargazers_count',
            'fork': 'forks_count'
        }

        key, operator, value = match.groups()
        field = field_map[key]
        value = int(value)

        with open(self.json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)['data']
            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                return

        op_func = {
            '>': lambda x: x > value,
            '<': lambda x: x < value,
            '>=': lambda x: x >= value,
            '<=': lambda x: x <= value,
            '=': lambda x: x == value,
        }[operator]

        print(f"[SEARCH] Filtering repos where {field} {operator} {value}:")
        for layer in data:
            for repo in layer:
                count = repo.get(field, 0)
                if isinstance(count, int) and op_func(count):
                    self.print_repo(repo)

    def print_repo(self, repo):
        print(f"- {repo.get('full_name')} | ⭐ {repo.get('stargazers_count', 0)} | 🍴 {repo.get('forks_count', 0)} | 🖥️ {repo.get('language')} | 📜 {repo.get('description')}")

    def graphy(self, _):
        if not os.path.exists(self.csv_path):
            print(f"[ERROR] CSV file not found: {self.csv_path}")
            return

        names, stars, forks, languages = [], [], [], []

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                names.append(row['full_name'])
                stars.append(int(row.get('stargazers_count', 0)))
                forks.append(int(row.get('forks_count', 0)))
                lang = row.get('language', '') or "Unknown"
                languages.append(lang)

        total_repos = len(names)
        if total_repos == 0:
            print("[ERROR] No data found in CSV.")
            return

 
        width_per_repo = 0.5
        fig_width = max(12, total_repos * width_per_repo)
        font_size = 10 if total_repos <= 20 else max(5, 12 - (total_repos // 20))
 
        plt.figure(figsize=(fig_width, 6))
        x = range(total_repos)
        plt.bar(x, stars, label='Stars', color='gold')
        plt.bar(x, forks, bottom=stars, label='Forks', color='skyblue')
        plt.xticks(x, names, rotation=90, fontsize=font_size)
        plt.title('Stars and Forks per Repository')
        plt.legend()
        plt.tight_layout()
        plt.show()

 
        lang_count = Counter(languages)
        plt.figure(figsize=(8, 8))
        plt.pie(lang_count.values(), labels=lang_count.keys(), autopct='%1.1f%%')
        plt.title('Language Distribution')
        plt.tight_layout()
        plt.show()

    def update_data(self, _):
        ip = input("[+] Proxy IP (default: none): ").strip() or None
        port_str = input("[+] Proxy Port (default: none): ").strip()
        port = int(port_str) if port_str else 0
        page_str = input("[+] Number of pages to update: ").strip()
        page_ = int(page_str) if page_str else 0

        gitrepo.github_repos(page=page_, proxy_ip=ip, proxy_port=port).run()

    def exit_cli(self, _):
        print("[*] Exiting GitAny.")
        exit(0)

def main():
    print(LOGO)
    cli = GitAny()
    cli.run()

if __name__ == "__main__":
    main()

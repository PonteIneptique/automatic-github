import requests
from sys import argv
import json
import os

import lines

def github_search(query, user, repo):
    page = 1
    items = list()
    total_results = 1

    url = "https://api.github.com/search/code"

    while len(items) < total_results:
        params = { 
            "q" : "{query} in:{repo} user:{user}".format(query=query.strip('"'), user=user, repo=repo),
            "page" : 1,
            "per_page" : 100
        }
        search = requests.get(url, params=params)
        print(search.url)
        results = search.json()

        total_results = results["total_count"]

        for r in results["items"]:

            ns = repo.split("-")[-1]
            urn  = "urn:cts:{ns}:{filename}".format(ns=ns, filename= ".".join(r["name"].split(".")[0:-1]))

            items.append({
                "score" : r["score"],
                "name" : r["name"],
                "path" : r["path"],
                "urn" : urn,
                "download" : r["html_url"].replace("blob/", "").replace("github.com", "raw.githubusercontent.com")
               # "download" : 
            })

        page += 1

    os.makedirs("cache", exist_ok=True)
    with open("cache/result.json", "w") as f:
        json.dump(items, f)

    for item in items:
        print("Processing : " + item["name"])
        lines.transform_lines(item["download"])


if __name__ == '__main__':
    github_search(*tuple(argv[1:]))

#%3Cstep+refunit%3D%22line%22+from%3D%22DESCENDANT+%281+L+N%251%29%22+to%3D%22DITTO%22%2F%3E"+"in:canonical-greekLit"+user:perseusDL
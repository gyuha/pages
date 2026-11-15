#!/usr/bin/env python3
"""GitHub Pages 사이트를 수집해 _data/sites.yml과 비교합니다.

사용 예:
    python3 scripts/discover-pages.py
    python3 scripts/discover-pages.py --check
    python3 scripts/discover-pages.py --check --json

--check 를 주면 각 사이트에 실제로 접속해 HTTP 상태와 페이지 제목을 확인합니다.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "_data" / "sites.yml"
API = "https://api.github.com"
WORKERS = 8

# 이 페이지 자체(디렉터리 저장소)는 목록에 넣지 않습니다.
EXCLUDED_REPOS = {"pages"}


def fail(message):
    print(f"오류: {message}", file=sys.stderr)
    sys.exit(1)


def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    try:
        return subprocess.check_output(
            ["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        fail("GitHub 토큰을 찾을 수 없습니다. `gh auth login`을 실행하거나 GITHUB_TOKEN을 설정하세요.")


def api_get(url, token):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "gyuha-pages-directory",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 403:
            fail("GitHub API rate limit에 걸렸습니다. 잠시 후 다시 시도하세요.")
        raise


def get_owner():
    token = get_token()
    return api_get(f"{API}/user", token)["login"], token


def list_owned_repos(token):
    repos = []
    page = 1
    while True:
        batch = api_get(
            f"{API}/user/repos?per_page=100&affiliation=owner&sort=updated&page={page}",
            token,
        )
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def get_pages_site(owner, repo_name, token):
    url = f"{API}/repos/{owner}/{urllib.parse.quote(repo_name)}/pages"
    try:
        return api_get(url, token)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def read_listed_urls():
    if not DATA_FILE.exists():
        return set()
    text = DATA_FILE.read_text(encoding="utf-8")
    urls = set()
    for match in re.finditer(r"^\s*url:\s*[\"']?(https?://[^\"'\s]+)", text, re.M):
        urls.add(match.group(1).rstrip("/"))
    return urls


def check_live(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (pages-directory)"}
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read(200_000).decode("utf-8", "ignore")
            title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            return response.status, html.unescape(title.group(1).strip()) if title else ""
    except urllib.error.HTTPError as error:
        return error.code, ""
    except Exception as error:  # DNS 실패 등
        return None, str(error)


def main():
    parser = argparse.ArgumentParser(description="GitHub Pages 사이트 수집")
    parser.add_argument("--check", action="store_true", help="실제 사이트 접속 상태 확인")
    parser.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = parser.parse_args()

    owner, token = get_owner()
    repos = list_owned_repos(token)
    public_repos = [
        repo
        for repo in repos
        if not repo["private"] and repo["name"] not in EXCLUDED_REPOS
    ]

    with ThreadPoolExecutor(WORKERS) as pool:
        pages_results = list(
            pool.map(lambda repo: get_pages_site(owner, repo["name"], token), public_repos)
        )

    sites = []
    for repo, pages in zip(public_repos, pages_results):
        if not pages or not pages.get("html_url"):
            continue
        sites.append(
            {
                "name": repo["name"],
                "url": pages["html_url"].replace("http://", "https://", 1).rstrip("/") + "/",
                "description": repo.get("description") or "",
                "language": repo.get("language") or "",
                "updated_at": repo.get("updated_at") or "",
                "status": pages.get("status"),
            }
        )
    sites.sort(key=lambda site: site["updated_at"], reverse=True)

    if args.check:
        with ThreadPoolExecutor(WORKERS) as pool:
            checks = list(pool.map(lambda site: check_live(site["url"]), sites))
        for site, (status, title) in zip(sites, checks):
            site["http_status"] = status
            site["page_title"] = title

    listed_urls = read_listed_urls()
    discovered_urls = {site["url"].rstrip("/") for site in sites}

    for site in sites:
        site["listed"] = site["url"].rstrip("/") in listed_urls

    new_sites = [site for site in sites if not site["listed"]]
    missing_urls = sorted(listed_urls - discovered_urls)
    broken = [
        site
        for site in sites
        if args.check and (site["http_status"] is None or site["http_status"] >= 400)
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "owner": owner,
                    "total_repos": len(repos),
                    "public_repos": len(public_repos),
                    "pages_sites": len(sites),
                    "listed_in_data_file": len(listed_urls),
                    "new_sites": new_sites,
                    "missing_urls": missing_urls,
                    "broken_sites": broken,
                    "sites": sites,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print(
        f"GitHub Pages 사이트 {len(sites)}개 "
        f"(공개 저장소 {len(public_repos)} / 전체 {len(repos)})"
    )

    print(f"\n[신규] {len(new_sites)}개 — _data/sites.yml에 없음")
    if not new_sites:
        print("  없음")
    for site in new_sites:
        print(f"  + {site['name']}  {site['url']}")
        if site["description"]:
            print(f"    {site['description']}")
        if site.get("page_title"):
            print(f"    title: {site['page_title']}")

    print(f"\n[목록에만 있음] {len(missing_urls)}개 — Pages 사이트를 찾지 못함")
    if not missing_urls:
        print("  없음")
    for url in missing_urls:
        print(f"  - {url}")

    if args.check:
        print(f"\n[접속 실패] {len(broken)}개")
        if not broken:
            print("  없음")
        for site in broken:
            print(f"  ! {site['name']}  {site['url']}  ({site['http_status'] or site['page_title']})")

    print(f"\n[전체 목록] {len(sites)}개")
    for site in sites:
        mark = " " if site["listed"] else "*"
        status = ""
        if args.check:
            status = f"  [{site['http_status'] or 'ERR'}]"
        print(f"  {mark} {site['name']:<28} {site['url']}{status}")

    print("\n* 표시는 _data/sites.yml에 없는 새 사이트입니다.")


if __name__ == "__main__":
    main()

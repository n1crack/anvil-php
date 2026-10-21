#!/usr/bin/env python3
"""Prints the PHP versions to build as a JSON list: the newest release of each
minor that has no GitHub release here yet.

Stable versions come from php.net's releases JSON. A minor with no stable
release yet (8.6) uses the newest php-src tag, built from the tarball php.net
lists for it on its pre-release page.

Usage: plan.py [minor,minor...]   (default: all)
       plan.py test
"""
import json
import re
import subprocess
import sys
import urllib.request

MINORS = ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "anvil-php"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def tag_key(v):
    # 8.6.0alpha1 < 8.6.0beta3 < 8.6.0RC4 < 8.6.0
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:(alpha|beta|RC)(\d+))?", v)
    if not m:
        return None
    stage = {"alpha": 0, "beta": 1, "RC": 2, None: 3}[m[4]]
    return (int(m[1]), int(m[2]), int(m[3]), stage, int(m[5] or 0))


def stable(minor):
    d = get(f"https://www.php.net/releases/index.php?json&version={minor}")
    if "version" not in d:
        return None
    v = d["version"]
    src = next(s for s in d["source"] if s["filename"] == f"php-{v}.tar.xz")
    return {"version": v, "minor": minor, "preview": False,
            "url": f"https://www.php.net/distributions/php-{v}.tar.xz", "sha256": src["sha256"]}


def preview(minor):
    refs = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/php/php-src/git/matching-refs/tags/php-{minor}."]))
    tags = [r["ref"].removeprefix("refs/tags/php-") for r in refs]
    tags = [t for t in tags if tag_key(t)]
    if not tags:
        return None
    v = max(tags, key=tag_key)
    pre = get("https://www.php.net/pre-release-builds.php?format=json").get("releases", {})
    xz = next((r["files"]["xz"] for r in pre.values() if r.get("version") == v), None)
    if not xz:
        # The tag is out but php.net has no tarball for it yet; try again tomorrow.
        print(f"php-{v}: tagged, no tarball on php.net yet", file=sys.stderr)
        return None
    return {"version": v, "minor": minor, "preview": True, "url": xz["path"], "sha256": xz["sha256"]}


def main():
    if sys.argv[1:] == ["test"]:
        order = ["8.6.0alpha1", "8.6.0alpha3", "8.6.0beta1", "8.6.0RC1", "8.6.0RC10", "8.6.0"]
        assert sorted(reversed(order), key=tag_key) == order
        assert tag_key("8.6.0-dev") is None
        print("ok")
        return
    only = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] else MINORS
    published = set(subprocess.check_output(
        ["gh", "release", "list", "--limit", "1000", "--json", "tagName", "--jq", ".[].tagName"],
        text=True).split())
    todo = []
    for minor in only:
        b = stable(minor) or preview(minor)
        if b and f"php-{b['version']}" not in published:
            todo.append(b)
    print(json.dumps(todo))


main()

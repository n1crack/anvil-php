#!/usr/bin/env python3
"""Puts one published build into index.json.

Usage: index.py <one build from plan.py, JSON> <SHA256SUMS>
"""
import json
import sys

build, sums = json.loads(sys.argv[1]), sys.argv[2]
version, minor = build["version"], build["minor"]
base = f"https://github.com/n1crack/anvil-php/releases/download/{build['tag']}"
prefix = f"php-{version}-"
files = {}
for line in open(sums):
    sha, name = line.split()
    key = name.removeprefix(prefix).removesuffix(".tar.gz")  # e.g. cli-macos-aarch64
    files[key] = {"url": f"{base}/{name}", "sha256": sha}

try:
    index = json.load(open("index.json"))
except FileNotFoundError:
    index = {}
# "build": Anvil installs the same version again when it grows. Older Anvils ignore it.
index[minor] = {"version": version, "preview": build["preview"], "build": build["build"],
                "files": dict(sorted(files.items()))}
with open("index.json", "w") as f:
    json.dump(dict(sorted(index.items())), f, indent=2)
    f.write("\n")

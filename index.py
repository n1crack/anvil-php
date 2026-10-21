#!/usr/bin/env python3
"""Puts one published build into index.json.

Usage: index.py <version> <minor> <preview:true|false> <SHA256SUMS>
"""
import json
import sys

version, minor, preview, sums = sys.argv[1:]
base = f"https://github.com/n1crack/anvil-php/releases/download/php-{version}"
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
index[minor] = {"version": version, "preview": preview == "true", "files": dict(sorted(files.items()))}
with open("index.json", "w") as f:
    json.dump(dict(sorted(index.items())), f, indent=2)
    f.write("\n")

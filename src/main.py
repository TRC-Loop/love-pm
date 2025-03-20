#!/usr/bin/env python3

import sys
import requests
from tqdm import tqdm
import tempfile
import os.path
import uuid
import json
import zipfile
import timeit
import shutil

temp_dir = tempfile.gettempdir()
current_dir = os.getcwd()
repo = "https://api.github.com/repos/TRC-Loop/love-pm-registry/contents/"

def download(url: str, fname: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def get_extension_from_url(url: str) -> str:
    _, extension = os.path.splitext(url)
    return extension

def get_download_link(repo, filename_no_ext):
    response = requests.get(repo)
    data = response.json()

    for item in data:
        if item['type'] == 'file':
            name, _ = os.path.splitext(item['name'])
            if name == filename_no_ext:
                return item['download_url']
    return None

def install(package_slug: str):
    print("Installing: " + package_slug)
    
    start = timeit.default_timer()
    print("Fetching Packages")
    
    link = get_download_link(repo, package_slug)
    
    if not link:
        print(f"Package '{package_slug}' doesn't exist.")
        sys.exit(-1)

    if not get_extension_from_url(link) == ".love_packagem":
        print("Invalid Package.")
        sys.exit(-1)
    
    loc = os.path.join(temp_dir, "love-pm", uuid.uuid4().hex + ".zip")
    extracted_loc = os.path.join(temp_dir, "love-pm", os.path.splitext(os.path.basename(loc))[0])
    os.makedirs(os.path.dirname(loc), exist_ok=True)
    os.makedirs(os.path.dirname(extracted_loc), exist_ok=True)
    print("Downloading: " + package_slug)
    download(link, loc)
    
    print("Extracting Package")
    with zipfile.ZipFile(loc, 'r') as zip_ref:
        zip_ref.extractall(extracted_loc)
    
    print("Reading Config")
    prop_json = os.path.join(extracted_loc, "prop.json")
    
    if not os.path.exists(prop_json):
        print("prop.json not found in: " + extracted_loc)
        print("Invalid package!")
        sys.exit(-1)
        
    properties: dict = None
    
    with open(prop_json, "r") as f:
        properties = json.load(f)
        
    if not "name" in properties.keys():
        print("Invalid Properties")
        sys.exit(-1)
    if not "version" in properties.keys():
        print("Invalid Properties")
        sys.exit(-1)
    
    print(f"Installing: '{properties['name']}' v{str(properties['version'])} to current project.")
    packages_dir = os.path.join(current_dir, "packages", properties["name"])
    os.makedirs(packages_dir, exist_ok=True)
    packages_file = os.path.join(current_dir, "packages", "index.json")
    
    if not os.path.exists(os.path.join(extracted_loc, "src")):
        print("Invalid Package!")
        sys.exit(-1)
    
    if os.path.exists(packages_file):
        with open(packages_file, "r") as f:
            data = json.load(f)
        if properties["name"] in [item["name"] for item in data]:
            print("Package already installed.")
            sys.exit(-1)
    
    shutil.copytree(os.path.join(extracted_loc, "src"), packages_dir, dirs_exist_ok=True)
    
    print("Updating Package List")
    
    if not os.path.exists(packages_file):
        with open(packages_file, "w") as f:
            json.dump([], f)

    with open(packages_file, "r+") as f:
        index = json.load(f)
        properties["slug"] = package_slug
        index.append(properties)
        f.seek(0)
        json.dump(index, f)
        f.truncate()
    
    end = timeit.default_timer()
    
    print("Successfully installed: " + properties["name"] + " in " + str(abs(round(start - end, 2))) + "s to " + packages_dir)

def uninstall(package_slug: str):
    print("Uninstalling: " + package_slug)
    
    packages_file = os.path.join(current_dir, "packages", "index.json")
    if not os.path.exists(packages_file):
        print("No packages installed.")
        sys.exit(-1)

    with open(packages_file, "r") as f:
        index = json.load(f)

    package = next((item for item in index if item["slug"] == package_slug), None)
    if not package:
        print(f"Package '{package_slug}' not found.")
        sys.exit(-1)

    # Remove package directory
    package_dir = os.path.join(current_dir, "packages", package["name"])
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
        print(f"Package '{package['name']}' removed from the filesystem.")
    
    # Remove package from the index.json
    index = [item for item in index if item["slug"] != package_slug]
    
    with open(packages_file, "w") as f:
        json.dump(index, f, indent=4)

    print(f"Package '{package['name']}' uninstalled successfully.")

def list_installed_packages():
    packages_file = os.path.join(current_dir, "packages", "index.json")
    if not os.path.exists(packages_file):
        print("No packages installed.")
        sys.exit(-1)
    
    with open(packages_file, "r") as f:
        index = json.load(f)
    
    if not index:
        print("No packages installed.")
    else:
        print("Installed Packages:")
        for package in index:
            print(f"{package['name']} ({package['slug'] if package['slug'] else "N/A"}) - v{package['version']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments provided")
        sys.exit(-1)
        
    command = sys.argv[1]
    
    if command == "list":
        list_installed_packages()
        sys.exit(0)
        
    if len(sys.argv) == 3:
        if command == "install":
            install(sys.argv[2])
            sys.exit(0)
        elif command == "uninstall":
            uninstall(sys.argv[2])
            sys.exit(0)
        else:
            print("Not a valid command")
            sys.exit(-1)
    else:
        print("Not a valid command")
        sys.exit(-1)

import os
import requests
import zipfile
import shutil
import asyncio
import aiohttp

from helpers import *
from constant import LethalConstant 
from aiohttp.client import ClientSession
from easygui import diropenbox
from abc import ABC, abstractmethod

CONS = LethalConstant()


# Abstract classes in case i can think of other ways to get information
class GetLocalVersion(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass
    @abstractmethod
    def get_version(self, mod_name: str) -> str:
        pass

class GetLatestVersion(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass
    @abstractmethod
    def get_version(self, mod_name: str) -> str:
        pass

class GetModInfo(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass
    @abstractmethod
    def get_container(self) -> dict:
        pass


class GetLocalVersionManifest(GetLocalVersion):
    def __init__(self, game_path, test_mode = False) -> None:
        self.game_path = game_path
        self.local_version = {}
        self.search_manifest_bepinex(test_mode)
        
    def get_version(self, mod_name: str):
        if mod_name in self.local_version:
            local_version = self.local_version[mod_name]
            return local_version
        return False
        
    def search_manifest_bepinex(self, test_mode = False) -> None:
        path_to_scan = [self.game_path] if test_mode else [self.game_path, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME]
        for dirpath, dirnames, filenames in os.walk(os.path.join(*path_to_scan)):
            for filename in filenames:
                if filename == CONS.MANIFEST_FILE:
                    full_dirpath = os.path.join(dirpath, filename)
                    manifest = read_json(full_dirpath)
                    self.local_version[manifest[CONS.MANIFEST_MOD_NAME]] = manifest[CONS.MANIFEST_MOD_VERSION]

class GetLatestVersionThunder(GetLatestVersion):
    def __init__(self, container: dict) -> None:
        self.latest_version = {}
        self.container = container
        self.count = 0
        asyncio.run(self.search_all_versions())

    def get_version(self, mod_name: str) -> str:
        if mod_name in self.latest_version:
            return self.latest_version[mod_name]["version"]
    
    def get_download_url(self, mod_name: str) -> str:
        if mod_name in self.latest_version:
            return self.latest_version[mod_name]["download_url"]

    async def download_link(self, url:str,session:ClientSession, max_retries=10):
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                self.latest_version[result[CONS.THUNDER_MOD_NAME]] = {
                    "version": result[CONS.THUNDER_LATEST][CONS.THUNDER_MOD_VERSION],
                    "download_url": result[CONS.THUNDER_LATEST][CONS.THUNDER_MOD_URL]
                }
                self.count += 1
                print(f"\rAnalyzing mods ({self.count}/{len(self.container)})", flush=True, end="")
                
            elif response.status == 429:
                if max_retries > 0:
                    await asyncio.sleep(2) 
                    await self.download_link(url, session, max_retries - 1)
                else:
                    print("FATAL ERROR")

    async def search_all_versions(self, limit = 5):
        my_conn = aiohttp.TCPConnector(limit=limit)
        async with aiohttp.ClientSession(connector=my_conn) as session:
            tasks = []
            for name, author in self.container.items():
                url = f"https://thunderstore.io/api/experimental/package/{author}/{name}/"
                task = asyncio.ensure_future(self.download_link(url=url,session=session))
                tasks.append(task)
            await asyncio.gather(*tasks,return_exceptions=True) # the await must be nest inside of the session

class GetModInfoYML(GetModInfo):
    def __init__(self) -> None:
        self.mods = {}

    def get_container(self) -> dict:
        if self.mods == {}:
            yml = self.__get_yml_local()
            if not yml:
                yml = self.__get_yml_github()
            for mod in yml:
                self.mods[mod["displayName"]] = mod["authorName"]
            return self.mods
        return self.mods

    def __get_yml_github(self) -> yaml:
        request = requests.get(CONS.YML_GITHUB_URL)
        if request.status_code == 200:
            file = yaml.safe_load(request.text)
            return file
        raise request

    def __get_yml_local(self) -> yaml:
        listdir = os.listdir(os.curdir)
        lower_listdir = [file.lower() for file in listdir]
        if CONS.YML_FILE_NAME in lower_listdir:
            with open(CONS.YML_FILE_NAME, "r") as file:
                return yaml.safe_load(file)
        return False            
    
class SearchMods:
    def __init__(self, local_version: GetLocalVersionManifest, latest_version: GetLatestVersionThunder) -> None:
        self.local_version = local_version
        self.latest_version = latest_version

        self.outdated_mod = []
        self.missing_mod = []
        self.extra_mod = []

    def is_outdated_mod(self, mod_name: str) -> bool:
        local_version = self.local_version.get_version(mod_name)
        latest_version = self.latest_version.get_version(mod_name)

        if local_version != latest_version:
            self.outdated_mod.append(mod_name)
            return True
        return False
    
    def is_missing_mod(self, mod_name: str) -> bool:
        response = self.local_version.get_version(mod_name)
        if not response:
            self.missing_mod.append(mod_name)
            return True
        return False
    
    def is_extra_mod(self, mod_name: str, container: dict) -> bool:
        if mod_name in container:
            return False
        self.extra_mod.append(mod_name)
        return True

class DownloadManager:
    def __init__(self, game_path) -> None:
        self.game_path = game_path

    def download_mod(self, mod_name: str, download_url: str) -> None:
        while True:
            request = requests.get(download_url, allow_redirects=True)
            if request.status_code == 200:
                path = os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, mod_name)
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(path+".zip", "wb+") as file:
                    for chunk in request.iter_content(chunk_size=128):
                        if chunk:
                            file.write(chunk)
                break

    def extract_mod(self, mod_name: str, extract_to: str) -> str:
        with zipfile.ZipFile(os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, mod_name+".zip"), "r") as extract:
            extract.extractall(extract_to)
        
    def delete_mod(self, mod_name: str) -> None:
        path = os.path.join(self.game_path, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME)
        listdir = os.listdir(path)
        for i in listdir:
            author = i.split("-")[0]
            mod_path = os.path.join(path, author+"-"+mod_name)
            if os.path.exists(mod_path):
                shutil.rmtree(mod_path) 

# Class in charge of entering the mods into Lethal Company folder.
class FilesManagerLethal:
    def __init__(self, game_path) -> None:
        self.game_path = game_path

    def move_dirs(self, fullname_mod: str, mod_path: str, *destination_path: str) -> None:
        bepinex_folder = os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, fullname_mod)
        destination_path = os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, *destination_path)

        if not os.path.exists(destination_path):
            os.makedirs(bepinex_folder, exist_ok=True)
            os.makedirs(destination_path, exist_ok=True)
        listdir = os.listdir(mod_path)

        for dirname in listdir:
            file_path = os.path.join(mod_path, dirname)
            shutil.move(file_path, destination_path)
        
        shutil.copytree(bepinex_folder, self.game_path, dirs_exist_ok=True)
        
    def move_files(self, fullname_mod: str, mod_path: str, *destination_path: str):
        bepinex_folder = os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, fullname_mod)
        destination_path = os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, *destination_path)

        if not os.path.exists(destination_path):
            os.makedirs(bepinex_folder, exist_ok=True)
            os.makedirs(destination_path, exist_ok=True)
        listdir = os.listdir(mod_path)

        for dirname in listdir:
                file_path = os.path.join(mod_path, dirname)
                if os.path.isfile(file_path):
                    shutil.move(file_path, destination_path)
        
        shutil.copytree(bepinex_folder, self.game_path, dirs_exist_ok=True)

    def process_folder(self, mod_path: str, fullname_mod: str):
        listdir = os.listdir(mod_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]

        if CONS.MANIFEST_FILE in lower_listdir:
            self.is_manifest(mod_path, fullname_mod)

        listdir = os.listdir(mod_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]

        for file in lower_listdir:
            if file.endswith(".dll"):
                self.is_dll(mod_path, fullname_mod)
        
        listdir = os.listdir(mod_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]

        if listdir != []:
            if CONS.BEPINEX_NAME.lower() in lower_listdir:
                self.is_bepinex(mod_path, fullname_mod)
                return
            if CONS.PLUGINS_NAME.lower() in lower_listdir:
                self.is_plugins(mod_path, fullname_mod)
            if CONS.PATCHERS_NAME.lower() in lower_listdir:
                self.is_patchers(mod_path, fullname_mod)
            if CONS.CORE_NAME.lower() in lower_listdir:
                self.is_core(mod_path, fullname_mod)
            if CONS.CONFIG_NAME.lower() in lower_listdir:
                self.is_config(mod_path, fullname_mod)
    
            names_to_check = [CONS.CORE_NAME.lower(), CONS.PATCHERS_NAME.lower(), CONS.PLUGINS_NAME.lower(), CONS.BEPINEX_NAME.lower(), CONS.CONFIG_NAME.lower()]
            if any(not name in names_to_check for name in lower_listdir):
                self.is_other(mod_path, fullname_mod)
    
    def is_bepinex(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, CONS.BEPINEX_NAME)
        if CONS.BEPINEX_NAME.lower() in fullname_mod.lower():
            self.move_dirs(fullname_mod, completed_path, fullname_mod, CONS.BEPINEX_NAME)
        self.process_folder(completed_path, fullname_mod)
    
    def is_plugins(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, CONS.PLUGINS_NAME)
        listdir = os.listdir(completed_path)
        if len(listdir) != 1:
            self.process_folder(completed_path, fullname_mod)
        else:
            self.move_dirs(fullname_mod, completed_path, fullname_mod, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME, fullname_mod)

    def is_core(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, CONS.CORE_NAME)
        self.move_dirs(fullname_mod, completed_path, fullname_mod, CONS.BEPINEX_NAME, CONS.CORE_NAME, fullname_mod)
        shutil.rmtree(completed_path)

    def is_patchers(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, CONS.PATCHERS_NAME)
        self.move_dirs(fullname_mod, completed_path, fullname_mod, CONS.BEPINEX_NAME, CONS.PATCHERS_NAME, fullname_mod)
        shutil.rmtree(completed_path)

    def is_config(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, CONS.CONFIG_NAME)
        self.move_dirs(fullname_mod, completed_path, fullname_mod, CONS.BEPINEX_NAME, CONS.CONFIG_NAME)
        shutil.rmtree(completed_path)

    def is_dll(self, mod_path: str, fullname_mod):
        listdir = os.listdir(mod_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]
        if CONS.BEPINEX_NAME.lower() in lower_listdir:
            self.move_files(fullname_mod, mod_path, fullname_mod)
        else:
            self.move_dirs(fullname_mod, mod_path, fullname_mod, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME, fullname_mod)

    def is_manifest(self, mod_path: str, fullname_mod: str):
        into_mod = os.path.join(self.game_path, CONS.TEMPORAL_FOLDER, fullname_mod, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME, fullname_mod)
        if not os.path.exists(into_mod):
            self.move_files(fullname_mod, mod_path, fullname_mod, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME, fullname_mod)

    def is_other(self, mod_path: str, fullname_mod):
        listdir = os.listdir(mod_path)
        count_dirs = len(listdir)

        for i in listdir:
            if not os.path.isfile(os.path.join(mod_path, i)) and count_dirs == 1:
                completed_path = os.path.join(mod_path, *listdir)
                self.process_folder(completed_path, fullname_mod)
                return

        self.move_dirs(fullname_mod, mod_path, fullname_mod, CONS.BEPINEX_NAME, CONS.PLUGINS_NAME, fullname_mod)

def start() -> str:
    while True:
        path = diropenbox("Select the Lethal Company folder")
        listdir = os.listdir(path)
        for file in listdir:
            if file.endswith(".exe"):
                os.system("cls")
                return path
        print("Please select the folder where the .exe is located")

def main():
    game_path = start()
    local_version = GetLocalVersionManifest(game_path)
    get_mod_info = GetModInfoYML()
    container = get_mod_info.get_container()
    latest_version = GetLatestVersionThunder(container)
    os.system("cls")
    print("Done!")
    get_mod_info = GetModInfoYML()
    search_mods = SearchMods(local_version, latest_version)
    download_manager = DownloadManager(game_path)
    move_files = FilesManagerLethal(game_path)

    # TODO use this iteration to then put imgui.
    
    print("\r\nVerifying mods...")

    total_mods = local_version.local_version | container

    for name in total_mods:
        if search_mods.is_extra_mod(name, container):
            print("-"+name, "EXTRA")
            continue

        if search_mods.is_missing_mod(name):
            print("-"+name, "MISSING")
            continue

        if search_mods.is_outdated_mod(name):
            print("-"+name, "OUTDATED")
            continue

    # The other iteration is not used to download and delete for better presentation.
    total_mods = search_mods.outdated_mod + search_mods.missing_mod
    
    if total_mods != []:
        print("\r\nInstalling mods...")
        for num, mod_name in enumerate(total_mods):

            author = container[mod_name]
            fullname = author +"-"+ mod_name

            extract_path = os.path.join(game_path, CONS.TEMPORAL_FOLDER, mod_name)
            refactorized_path = os.path.join(game_path, CONS.TEMPORAL_FOLDER, fullname)

            download_manager.download_mod(mod_name, latest_version.get_download_url(mod_name))
            download_manager.extract_mod(mod_name, extract_path)
            move_files.process_folder(extract_path, fullname)

            print("-"+mod_name, "INSTALLED", f"({num + 1}/{len(total_mods)})")

            shutil.rmtree(extract_path)
            shutil.rmtree(refactorized_path)
            os.remove(extract_path+".zip")
        shutil.rmtree(os.path.join(game_path, CONS.TEMPORAL_FOLDER))

    if search_mods.extra_mod != []:
        print("\r\nUnistalling mods...")
        for mod_name in search_mods.extra_mod:
            question = input(f"¿Deseas eliminar este mod: {mod_name} (y/n)?")
            if question == "n":
                pass
            else:
                download_manager.delete_mod(mod_name)

if __name__ == "__main__":
    main()
    input("\r\nPRESIONE ENTER PARA CONTINUAR")
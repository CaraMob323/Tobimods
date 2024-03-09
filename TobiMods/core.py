import os
import requests
import zipfile
import shutil
import asyncio
import time
import aiohttp

from helpers import *
from constant import LethalConstant 
from aiohttp.client import ClientSession
from easygui import diropenbox
from abc import ABC, abstractmethod

constant = LethalConstant()


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
        path_to_scan = [self.game_path] if test_mode else [self.game_path, constant.BEPINEX_NAME, constant.PLUGINS_NAME]
        for dirpath, dirnames, filenames in os.walk(os.path.join(*path_to_scan)):
            for filename in filenames:
                if filename == constant.MANIFEST_NAME:
                    full_dirpath = os.path.join(dirpath, filename)
                    manifest = read_json(full_dirpath)
                    self.local_version[manifest["name"]] = manifest["version_number"]

class GetLatestVersionThunder(GetLatestVersion):
    def __init__(self, container: dict) -> None:
        self.latest_version = {}
        self.container = container
        asyncio.run(self.search_all_versions())

    def get_version(self, mod_name: str) -> str:
        if mod_name in self.latest_version:
            return self.latest_version[mod_name]["version"]
    
    def get_download_url(self, mod_name: str) -> str:
        if mod_name in self.latest_version:
            return self.latest_version[mod_name]["download_url"]

    async def download_link(self, url:str,session:ClientSession, max_retries=4):
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                print(result["name"], "ANALIZADO")
                self.latest_version[result["name"]] = {
                    "version": result["latest"]["version_number"],
                    "download_url": result["latest"]["download_url"]
                }
            else:
                if max_retries > 0:
                    await asyncio.sleep(2) 
                    await self.download_link(url, session, max_retries - 1)
                else:
                    raise TimeoutError("API 429 ERROR")


    async def search_all_versions(self):
        my_conn = aiohttp.TCPConnector(limit=5)
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
            yml = self.__get_yml()
            for mod in yml:
                self.mods[mod["displayName"]] = mod["authorName"]
            with open("a.json", "w") as file:
                json.dump(self.mods, file, indent=4)
            return self.mods
        return self.mods

    def __get_yml(self) -> yaml:
        url = "https://raw.githubusercontent.com/CaraMob323/Tobimods/main/mods.yml"
        request = requests.get(url)
        if request.status_code == 200:
            file = yaml.safe_load(request.text)
            return file
        raise request

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

        if not local_version or latest_version == None or latest_version == "":
            return False

        if local_version != latest_version:
            self.outdated_mod.append(mod_name)
            return True
        return False
    
    def is_missing_mod(self, mod_name: str) -> bool:
        if not self.local_version.get_version(mod_name):
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
                path = os.path.join(self.game_path, mod_name)
                with open(path+".zip", "wb+") as file:
                    for chunk in request.iter_content(chunk_size=128):
                        if chunk:
                            file.write(chunk)
                break

    def extract_mod(self, mod_name: str, extract_to: str) -> str:
        with zipfile.ZipFile(os.path.join(self.game_path, mod_name+".zip"), "r") as extract:
            extract.extractall(extract_to)
        
    def delete_mod(self, mod_name: str) -> None:
        path = os.path.join(self.game_path, constant.BEPINEX_NAME, constant.PLUGINS_NAME)
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
        bepinex_folder = os.path.join(self.game_path, fullname_mod)
        destination_path = os.path.join(self.game_path, *destination_path)

        if not os.path.exists(destination_path):
            os.makedirs(bepinex_folder, exist_ok=True)
            os.makedirs(destination_path, exist_ok=True)
        listdir = os.listdir(mod_path)

        for dirname in listdir:
            if dirname.lower() != constant.PLUGINS_NAME:
                file_path = os.path.join(mod_path, dirname)
                shutil.move(file_path, destination_path)
        
        shutil.copytree(bepinex_folder, self.game_path, dirs_exist_ok=True)
        
    def move_files(self, fullname_mod: str, mod_path: str, *destination_path: str):
        bepinex_folder = os.path.join(self.game_path, fullname_mod)
        destination_path = os.path.join(self.game_path, *destination_path)

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

        if constant.MANIFEST_NAME in lower_listdir:
            self.is_manifest(mod_path, fullname_mod)

        for file in lower_listdir:
            if file.endswith(".dll"):
                self.is_dll(mod_path, fullname_mod)
        
        listdir = os.listdir(mod_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]

        if listdir != []:
            if constant.BEPINEX_NAME in lower_listdir:
                self.is_bepinex(mod_path, fullname_mod)
            elif constant.PLUGINS_NAME in lower_listdir:
                self.is_plugins(mod_path, fullname_mod)
            else:
                self.is_other(mod_path, fullname_mod)
    
    def is_bepinex(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, constant.BEPINEX_NAME)
        listdir = os.listdir(completed_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]

        if not constant.PLUGINS_NAME in lower_listdir:
            self.move_dirs(fullname_mod, completed_path, fullname_mod, constant.BEPINEX_NAME)
        elif len(lower_listdir) > 1 and constant.PLUGINS_NAME in lower_listdir:
            self.move_dirs(fullname_mod, completed_path, fullname_mod, constant.BEPINEX_NAME)
            self.process_folder(completed_path, fullname_mod)
        else:
            self.process_folder(completed_path, fullname_mod)
    
    def is_plugins(self, mod_path: str, fullname_mod):
        completed_path = os.path.join(mod_path, constant.PLUGINS_NAME)
        listdir = os.listdir(completed_path)
        if len(listdir) != 1:
            self.process_folder(completed_path, fullname_mod)
            return
        self.move_dirs(fullname_mod, completed_path, fullname_mod, constant.BEPINEX_NAME, constant.PLUGINS_NAME, fullname_mod)

    def is_dll(self, mod_path: str, fullname_mod):
        listdir = os.listdir(mod_path)
        lower_listdir = [dirfile.lower() for dirfile in listdir]
        if constant.BEPINEX_NAME in lower_listdir:
            self.move_files(fullname_mod, mod_path)
        else:
            self.move_dirs(fullname_mod, mod_path, fullname_mod, constant.BEPINEX_NAME, constant.PLUGINS_NAME, fullname_mod)

    def is_other(self, mod_path: str, fullname_mod):
        listdir = os.listdir(mod_path)
        if "config" in listdir:
            listdir.remove("config")
        count_dirs = len(listdir)

        for i in listdir:
            if not os.path.isfile(os.path.join(mod_path, i)) and count_dirs == 1:
                if "patchers" in listdir:
                    self.move_dirs(fullname_mod, mod_path, fullname_mod,  constant.BEPINEX_NAME)
                    return
                completed_path = os.path.join(mod_path, *listdir)
                self.process_folder(completed_path, fullname_mod)
                return

        self.move_dirs(fullname_mod, mod_path, fullname_mod, constant.BEPINEX_NAME, constant.PLUGINS_NAME, fullname_mod)

    def is_manifest(self, mod_path: str, fullname_mod: str):
        into_mod = os.path.join(self.game_path, fullname_mod, constant.BEPINEX_NAME, constant.PLUGINS_NAME, fullname_mod)
        if not os.path.exists(into_mod):
            self.move_files(fullname_mod, mod_path, fullname_mod, constant.BEPINEX_NAME, constant.PLUGINS_NAME, fullname_mod)


def main():
    game_path = diropenbox("Select the Lethal Company folder")
    local_version = GetLocalVersionManifest(game_path)
    get_mod_info = GetModInfoYML()
    container = get_mod_info.get_container()

    print("Searching latest versions...")
    latest_version = GetLatestVersionThunder(container)
    print("Done")
    get_mod_info = GetModInfoYML()
    search_mods = SearchMods(local_version, latest_version)
    download_manager = DownloadManager(game_path)
    move_files = FilesManagerLethal(game_path)

    print("\r\nVerifying mods...")
    
    # TODO use this iteration to then put imgui.
    for name in local_version.local_version:
        if search_mods.is_extra_mod(name, container):
            print(name, "EXTRA")

        if search_mods.is_outdated_mod(name):
            print(name, "OUTDATED")

        if search_mods.is_missing_mod(name):
            print(name, "MISSING")
            

    # The other iteration is not used to download and delete for better presentation.
    total_mods = search_mods.outdated_mod + search_mods.missing_mod
    if total_mods != []:
        print("\r\Installing mods...")
        for mod_name in total_mods:

            author = container[mod_name]
            fullname = author +"-"+ mod_name

            extract_path = os.path.join(game_path, mod_name)
            refactorized_path = os.path.join(game_path, fullname)

            download_manager.download_mod(mod_name, latest_version.get_download_url(mod_name))
            download_manager.extract_mod(mod_name, extract_path)
            move_files.process_folder(extract_path, fullname)

            shutil.rmtree(extract_path)
            shutil.rmtree(refactorized_path)
            os.remove(extract_path+".zip")

    if search_mods.extra_mod != []:
        print("\r\Unistalling mods...")
        for mod_name in search_mods.extra_mod:
            question = input(f"¿Deseas eliminar este mod: {mod_name} (y/n)?")
            if question == "n":
                pass
            else:
                download_manager.delete_mod(mod_name)

                
if __name__ == "__main__":
    main()
    input("\r\nPRESIONE ENTER PARA CONTINUAR")
    # end = time.time()

    # print("Tardo en instalar los mods un total de:", end - start, "segundos")
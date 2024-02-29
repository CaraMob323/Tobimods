import os
import requests
import zipfile
import shutil
from easygui import diropenbox
from concurrent.futures import ThreadPoolExecutor

import json
import yaml

def save_json(path: str, name: str, saved: str):
    with open(path+"\\"+name, "w+") as file:
        json.dump(saved, file, indent=4)

def read_json(path: str):
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)
    
def read_yaml(path: str):
    with open(path, "r") as file:
        return yaml.load(file, Loader = yaml.SafeLoader)
        

class GetFilesRules:
    def __init__(self) -> None:
        self.files_rules = {}
              
    def get_file_rules(self, path: str):
        for dirpath, dirnames, filenames in os.walk(os.path.join(path)):
            for item in filenames + dirnames:
                full_path = os.path.join(dirpath, item)
                dirlist = full_path.split(os.sep)
                mod_name = path.split("\\")[-1]
                if os.path.isfile(full_path) and item.endswith(".dll"):
                    self.files_rules[mod_name] = {
                        "path_.dll": full_path,
                        "path_bepinex": self.__get_rule_path(dirlist, "bepinex"),
                        "path_plugins": self.__get_rule_path(dirlist, "plugins"),
                        "path_manifest": None
                    }
                elif os.path.isdir(full_path) and full_path.split("\\")[-1].lower() == "plugins":
                        self.files_rules[mod_name] = {
                            "path_.dll": None,
                            "path_bepinex": self.__get_rule_path(dirlist, "bepinex"),
                            "path_plugins": self.__get_rule_path(dirlist, "plugins"),
                            "path_manifest": None
                        }

        for dirpath, dirnames, filenames in os.walk(os.path.join(path)):
            for filename in filenames:
                if filename == "manifest.json":
                    dirlist = dirpath.split(os.sep)
                    if mod_name in self.files_rules:
                        self.files_rules[mod_name]["path_manifest"] = os.path.join(dirpath, filename)
                    else:
                        self.files_rules[mod_name] = {
                            "path_.dll": None,
                            "path_bepinex": None,
                            "path_plugins": None,
                            "path_manifest": os.path.join(dirpath, filename)
                        }
                    
    def __get_rule_path(self, dirname: list, folder: str):
        lower_dirnames = [lower_dirname.lower() for lower_dirname in dirname]
        if folder in lower_dirnames:
            for i in range(len(dirname)):
                if lower_dirnames[i] == folder:
                    return os.path.join(*dirname[:i+1])
        else:
            return None        

class ManageFolders:
    def __init__(self) -> None:
        self.lethal_path = None
        self.search_folder()
        self.yml = self.get_mods_list()

    def search_folder(self):
        folder = diropenbox(title="Seleccione la carpeta de Lethal Company")
        if folder == "" or folder == None:
            raise FileNotFoundError("Seleccione una carpeta")
        self.lethal_path = folder

    def get_mods_list(self):
        url = "https://raw.githubusercontent.com/CaraMob323/Tobimods/main/mods.yml"
        request = requests.get(url)
        if request.status_code == 200:
            file = yaml.safe_load(request.text)
            return file
        raise request

class ManageCases: # I don't know as this works but works
    def __init__(self) -> None:
        self.manage_folders = ManageFolders()
        self.lethal_path = self.manage_folders.lethal_path
        self.rules = GetFilesRules()

    def choose_case(self, name: str, author: str):
        self.rules.get_file_rules(self.lethal_path+"\\"+name)
        manifest = self.rules.files_rules[name]["path_manifest"]
        pathlist = manifest.split("\\")
        full_name = author+"-"+pathlist[-2]
        pathlist = [x + "\\" for x in pathlist]
        pathlist = pathlist[:-1]
        path = os.path.join(*pathlist)
        if self.rules.files_rules[name]["path_bepinex"] == None:
            self.case_folder_dll(path, full_name)
        elif self.rules.files_rules[name]["path_bepinex"] != None and self.rules.files_rules[name]["path_plugins"] != None:
            self.case_bepinex_plugins_dll(path, full_name)
        else:
            self.case_bepinex_dll(path, full_name)
        shutil.rmtree(path)
        print(name, "se descargo bien xd")

    def case_bepinex_plugins_dll(self, path_folder: str, full_name: str):
        plugins_folder = path_folder+"BepInEx"+"\\"+"plugins"

        file_destination = plugins_folder+"\\"+full_name
        content_mod = os.listdir(path_folder)
        content_plugins = os.listdir(plugins_folder)

        os.makedirs(file_destination, exist_ok=True)

        for item in content_plugins:
            item_path = os.path.join(plugins_folder, item)
            shutil.move(item_path, file_destination)
        for item in content_mod:
            item_path = path_folder+"\\"+item
            if os.path.isfile(item_path):
                shutil.move(item_path, file_destination)

        shutil.copytree(path_folder, self.lethal_path, dirs_exist_ok=True)
    
    def case_folder_dll(self, path_folder: str, full_name: str):
        plugins_folder = path_folder+"plugins"

        os.makedirs(plugins_folder, exist_ok=True)
        file_destination = plugins_folder+"\\"+full_name
        content_mod = os.listdir(path_folder)
        content_plugins = os.listdir(plugins_folder)

        os.makedirs(file_destination, exist_ok=True)

        for item in content_plugins:
            item_path = os.path.join(plugins_folder, item)
            shutil.move(item_path, file_destination)
        for item in content_mod:
            item_path = path_folder+"\\"+item
            if os.path.isfile(item_path):
                shutil.move(item_path, file_destination)
            if os.path.isdir(item_path) and item[0].isupper():
                content = os.listdir(item_path)
                for item in content:
                    path = item_path+"\\"+item
                    if os.path.isdir(path):
                        if item == "plugins":
                            content = os.listdir(path)
                            for item in content:
                                item_path2 = path+"\\"+item
                                shutil.move(item_path2, file_destination)
                    else:
                        shutil.move(path, file_destination)
                shutil.rmtree(item_path)
                
        shutil.copytree(path_folder, f"{self.lethal_path}/BepInEx", dirs_exist_ok=True)

    def case_bepinex_dll(self, path_folder: str, full_name: str):
        plugins_folder = path_folder+"BepInEx"+"\\"+"plugins"
        bepinex_folder = path_folder+"BepInEx"
        os.makedirs(plugins_folder, exist_ok=True)

        file_destination = plugins_folder+"\\"+full_name
        content_mod = os.listdir(path_folder)

        os.makedirs(file_destination, exist_ok=True)
        files_moved = False
        for item in content_mod:
            item_path = path_folder+"\\"+item
            if os.path.isfile(item_path):
                shutil.move(item_path, file_destination)
                files_moved = True

            elif os.path.isdir(item_path) and item != "BepInEx":
                content = os.listdir(item_path)
                for item in content:
                    path = item_path+"\\"+item
                    if os.path.isfile(path) and "manifest.json" in content and files_moved == False:
                        shutil.move(path, file_destination)
                    elif os.path.isfile(path) and not "manifest.json" in content:
                        shutil.move(path, path_folder)
                    if os.path.isdir(path):
                        sub_content = os.listdir(path)
                        for sub_item in sub_content:
                            sub_path = path+"\\"+sub_item
                            if sub_item == "plugins":
                                sub_sub_content = os.listdir(sub_path)
                                for sub_sub_item in sub_sub_content:
                                    sub_sub_path = sub_path+"\\"+sub_sub_item
                                    shutil.move(sub_sub_path, file_destination)
                            else:
                                shutil.move(sub_path, bepinex_folder)
        
        for rest_item in content_mod:
            rest_path = path_folder+"\\"+rest_item
            if os.path.isdir(rest_path) and rest_item != "BepInEx":
                shutil.rmtree(rest_path)
                pass

    

        shutil.copytree(path_folder, self.lethal_path, dirs_exist_ok=True)


class IdentifyMods:
    def __init__(self) -> None:
        self.manage_cases = ManageCases()
        self.lethal_path = self.manage_cases.lethal_path

        self.missing_mods = []
        self.extra_mods = []
        self.outdated_mods = []
        self.information_mods = {}

    def identify_local_version(self):
        for dirpath, dirnames, filenames in os.walk(os.path.join(self.lethal_path, "BepInEx", "plugins")):
            for filename in filenames:
                if filename == "manifest.json":
                    path = os.path.join(dirpath, "manifest.json")
                    file = read_json(path)
                    self.information_mods.setdefault(file["name"], {}).update({
                        "author": "", 
                        "local_version": file["version_number"], 
                        "latest_version": ""
                    })

    def identify_latest_version(self):

        def process_mod(mod_name):
            if self.identify_extra_mods(mod_name) == False:
                url = f"https://thunderstore.io/api/experimental/package/{self.information_mods[mod_name]['author']}/{mod_name}/"
                response = requests.get(url)
                if response.status_code == 200:
                    json_mod = response.json()
                    self.information_mods[mod_name]["latest_version"] = json_mod["latest"]["version_number"]
                    self.information_mods[mod_name]["download_url"] = json_mod["latest"]["download_url"]
                    self.identify_outdated_mods(mod_name)
                    self.identify_missing_mods(mod_name)

                if response.status_code != 200:
                    print("INTENTA DE NUEVO, FALLO CATASTROFICO")

        with ThreadPoolExecutor(2) as executor:
            executor.map(process_mod, self.information_mods.keys())
        

    def identify_author_mods(self):
            mods: list = self.manage_cases.manage_folders.yml
            for mod_name in self.information_mods:
                for mod in mods:
                    if mod["displayName"] == mod_name:
                        mods.remove(mod)
                        self.information_mods[mod_name]["author"] = mod["authorName"]
            for mod in self.manage_cases.manage_folders.yml:
                self.missing_mods.append(mod["displayName"])
            for mod_name in self.missing_mods:
                for mod in mods:
                    if mod["displayName"] == mod_name:
                        self.information_mods.setdefault(mod_name, {}).update({"author": mod["authorName"], "local_version": "", "latest_version": ""})
            self.manage_cases.manage_folders.yml = self.manage_cases.manage_folders.get_mods_list()

    def identify_outdated_mods(self, mod_name):
        if self.information_mods[mod_name]["latest_version"] != self.information_mods[mod_name]["local_version"] and self.information_mods[mod_name]["local_version"] != "":
            self.outdated_mods.append(mod_name)
            print(mod_name, "TA DESACTUALIZADO")
        elif self.information_mods[mod_name]["local_version"] != "":
            print(mod_name, "ACTUALIZADO")

    def identify_missing_mods(self, mod_name: str):
        if self.information_mods[mod_name]["local_version"] == "":
            print(mod_name, "NO ESTA")

    def identify_extra_mods(self, mod_name):
            mod_exits: bool = False
            for mod in self.manage_cases.manage_folders.yml:
                if mod.get("displayName") == mod_name:
                    mod_exits = True
                    return False
            if mod_exits == False:
                print(mod_name, "EXTRA")
                self.extra_mods.append(mod_name)
                return True
    
class ManageMods:
    def __init__(self) -> None:
        self.identify = IdentifyMods()
        self.cases = self.identify.manage_cases

    def download_mod(self, url: str, name: str, path: str):
        while True:
            print(name, "Intentando descargar")
            request = requests.get(url, allow_redirects=True)
            if request.status_code == 200:
                path = os.path.join(path, name)
                with open(path + ".zip", "wb+") as file:
                    for chunk in request.iter_content(chunk_size=128):
                        if chunk:
                            file.write(chunk)
                break

    def extract_mod(self, name: str, path: str):
        with zipfile.ZipFile(path+"\\"+name+".zip", "r") as extract:
            extract.extractall(path+"\\"+name)

    def unistall_mod(self, mod_name):
        if mod_name in self.identify.extra_mods:
            for dirpath, dirnames, filenames in os.walk(os.path.join(self.identify.lethal_path, "BepInEx", "plugins")):
                for item in dirnames + filenames:
                    path: str = dirpath+"\\"+item
                    if os.path.isfile(path) and item == "manifest.json":
                        path_split = path.split("\\")
                        path_split = [x + "\\" for x in path_split]
                        pathlist = path_split[:-1]
                        final_path = os.path.join(*pathlist)
                        if pathlist[-1].split("-")[-1][:-1] == mod_name:
                            shutil.rmtree(final_path)
                            self.identify.extra_mods.remove(mod_name)
                            print("Desinstalado")
                            break

    def install_all(self):
        print("\r\nInstalando...")
        for mod_name in self.identify.outdated_mods + self.identify.missing_mods:
            self.download_mod(self.identify.information_mods[mod_name]["download_url"], mod_name, self.identify.lethal_path)
            self.extract_mod(mod_name, self.identify.lethal_path)
            os.remove(f"{self.identify.lethal_path}\\{mod_name}.zip")
            self.cases.choose_case(mod_name, self.identify.information_mods[mod_name]["author"])
        
        print("\r\nDesinstalando...")
        for mod_name in self.identify.extra_mods:
            question = input(f"QUERES DESINSTALAR ESTE MOD: {mod_name} (s/n): ")
            match question:
                case "s":
                    self.unistall_mod(mod_name)
                case "n":
                    pass
                case _:
                    self.unistall_mod(mod_name)

if "__main__" == __name__:
    test = ManageMods()
    print("Verificando mods...")
    test.identify.identify_local_version()
    test.identify.identify_author_mods()
    test.identify.identify_latest_version()
    test.install_all()
    input("PRESIONE ENTER PARA CERRAR")

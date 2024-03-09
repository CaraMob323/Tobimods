# def read():
#     with open("tests\mods_test\FlipMods-ReservedFlashlightSlot-1.6.3\ReservedFlashlightSlot.dll", "r", encoding="ANSI") as file:
#         return file.read()

# import re
# variable_buscada = "ReservedFlashlightSlot".lower()
import os

# def buscar_variable_y_secuencia(texto):
#     # Definir el patrón de búsqueda
#     patron = r'(\w+)\s+(\d+\.\d+\.\d+)'

#     # Buscar todas las coincidencias en el texto
#     coincidencias = re.findall(patron, texto)

#     # Mostrar las coincidencias encontradas
#     for coincidencia in coincidencias:
#         variable, secuencia = coincidencia
#         if variable_buscada in variable.lower():
#             print("Variable:", variable)
#             print("Secuencia:", secuencia)

# def eliminar_caracteres_especiales(cadena):
#     # Utilizamos una expresión regular para eliminar todos los caracteres especiales excepto el punto
#     cadena_limpia = re.sub(r'[^\w\s.]', '', cadena)
#     return cadena_limpia





# sin_caracteres = eliminar_caracteres_especiales(read())

# buscar_variable_y_secuencia(sin_caracteres)

# with open("save.txt", "w") as file:
#     file.write(sin_caracteres)


# from googlesearch import search
# import re
# import os

# results = search("detras del humo no se ve" + "thunderstore", num_results=1)

# a = next(results).split("/")
# print(a[-3])

# for a, b, c in os.walk("tests\\mods_test\\no"):
#     print(a)

import asyncio
import time
import aiohttp
from aiohttp.client import ClientSession

async def download_link(url:str,session:ClientSession):
    async with session.get(url) as response:
        result = await response.json()
        print(f'Read {len(result)} from {url}')

async def download_all(urls:dict):
    my_conn = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for author, name in urls.items():
            url = f"https://thunderstore.io/api/experimental/package/{author}/{name}/"
            task = asyncio.ensure_future(download_link(url=url,session=session))
            tasks.append(task)
        await asyncio.gather(*tasks,return_exceptions=True) # the await must be nest inside of the session


mods = {
    "BepInEx": "BepInExPack",
    "Rune580": "LethalCompany_InputUtils",
    "PotatoePet": "AdvancedCompany",
    "AlexCodesGames": "AdditionalContentFramework",
    "sunnobunno": "BonkHitSFX",
    "OnionMilk": "crosshair",
    "2018": "LC_API",
    "DerplingDevelopments": "SavageCompany",
    "x753": "More_Suits",
    "Bobbie": "NAudio",
    "qwbarch": "Mirage",
    "Evaisa": "LethalThings",
    "AllToasters": "QuickRestart",
    "Clementinise": "CustomSounds",
    "Hardy": "LCMaxSoundsFix",
    "no00ob": "LCSoundTool",
    "LethalResonance": "LETHALRESONANCE",
    "pap": "More_Suitspap",
    "Verity": "TooManySuits",
    "FlipMods": "TooManyEmotes",
    "TheDeadSnake": "Touchscreen",
    "BatTeam": "LethalFashion",
    "TwinDimensionalProductions": "CoilHeadStare",
    "FutureSavior": "Boombox_Sync_Fix",
    "Steven": "Custom_Boombox_Music",
    "CodeEnder": "Custom_Boombox_Fix",
    "ItzDannio25": "detras_del_humo_no_se_ve",
    "BabaTheSlime": "PushToMute",
    "Monkeytype": "HidePlayerNames",
    "ShaosilGaming": "GeneralImprovements",
    "Ozone": "Runtime_Netcode_Patcher",
    "Sligili": "More_Emotes",
    "notnotnotswipez": "MoreCompany",
    "IntegrityChaos": "GraphicsAPI",
    "itsmeowdev": "DoorFix",
    "PanHouse": "LethalClunk",
    "linkoid": "DissonanceLagFix",
    "HGG": "JigglePhysicsPlugin",
    "Mhz": "MoreHead",
    "ZachPlatypus": "FlashSuits",
    "My_Little_Team": "Arctic_Survival_Suit",
    "JoshPack": "Kratos",
    "Pee_John_Labs": "Fortnite_Fishstick",
    "doppelwrangler": "Gabriel_Suit",
    "MordenX": "KanamiReplacementMod",
    "Sai": "SaiCosmetics",
    "Kats": "Some_Suits",
    "Crab_imitation": "Reptilian_Suit",
    "happyfrosty": "FrostySuits",
    "ViViKo": "MoreMaterials",
    "fonnymunkey": "SimpleHats",
    "EliteMasterEric": "WackyCosmetics",
    "BunyaPineTree": "ModelReplacementAPI",
    "GhostbustingTrio": "CustomFunSuits",
    "Hexnet111": "SuitSaver",
    "PizzaTissa": "Gen2Replacement",
    "ExioMadeThis": "Ahegao_Suit",
    "Hypick": "TooManyCosmetics",
    "OnePeak": "Low_Budget_One_Piece_suits",
    "DrinkableWater": "Brutal_Company_Minus",
    "Solar32": "PerformanceEnhancer",
    "vasanex": "ItemQuickSwitch",
    "loaforc": "loaforcsSoundAPI",
    "jockie": "LethalExpansionCore",
    "rainbow137": "MinecraftScraps",
    "Zaggy1024": "OpenBodyCams",
    "MyGoofyLethalSounds": "MinecraftCompany_Doors",
    "netux": "Open_Doors_in_Space",
    "Epicool": "InsanityRemastered"
}

start = time.time()
asyncio.run(download_all(mods))
end = time.time()
print(f'download {len(mods)} links in {end - start} seconds')

import json, yaml, requests

class GetModInfoYML():
    def __init__(self) -> None:
        self.mods = {}

    def get_container(self) -> dict:
        if self.mods == {}:
            yml = self.__get_yml()
            count = 0
            print(len(yml))
            for mod in yml:
                count += 1

                self.mods[mod["displayName"]] = mod["authorName"] + f" {count}"

                print(self.mods[mod["displayName"]], len(self.mods))

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
    
a = GetModInfoYML()
a.get_container()
import unittest
import json
import os

from context import TobiMods

files_rules = TobiMods.core.GetFilesRules()
identify_mods = TobiMods.core.IdentifyMods()

class TestGetRules(unittest.TestCase):
    def test_get_rules(self):
        path = "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test"
        folders = os.listdir(path)
        expected_rules = {
            "BepInEx-BepInExPack-5.4.2100": {
                "path_.dll": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\BepInEx-BepInExPack-5.4.2100\\BepInExPack\\BepInEx\\core\\MonoMod.Utils.dll",
                "path_bepinex": "C:Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\BepInEx-BepInExPack-5.4.2100\\BepInExPack\\BepInEx",
                "path_plugins": None,
                "path_manifest": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\BepInEx-BepInExPack-5.4.2100\\manifest.json"
            },
            "Evaisa-HookGenPatcher-0.0.5": {
                "path_.dll": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\Evaisa-HookGenPatcher-0.0.5\\patchers\\BepInEx.MonoMod.HookGenPatcher\\MonoMod.RuntimeDetour.HookGen.dll",
                "path_bepinex": None,
                "path_plugins": None,
                "path_manifest": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\Evaisa-HookGenPatcher-0.0.5\\manifest.json"
            },
            "FlipMods-ReservedFlashlightSlot-1.6.3": {
                "path_.dll": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\FlipMods-ReservedFlashlightSlot-1.6.3\\ReservedFlashlightSlot.dll",
                "path_bepinex": None,
                "path_plugins": None,
                "path_manifest": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\FlipMods-ReservedFlashlightSlot-1.6.3\\manifest.json"
            },
            "IntegrityChaos-Diversity-2.0.0": {
                "path_.dll": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\IntegrityChaos-Diversity-2.0.0\\Diversity\\Diversity.dll",
                "path_bepinex": None,
                "path_plugins": None,
                "path_manifest": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\IntegrityChaos-Diversity-2.0.0\\manifest.json"
            },
            "Rune580-LethalCompany_InputUtils-0.6.3": {
                "path_.dll": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\Rune580-LethalCompany_InputUtils-0.6.3\\plugins\\LethalCompanyInputUtils\\LethalCompanyInputUtils.dll",
                "path_bepinex": None,
                "path_plugins": "C:Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\Rune580-LethalCompany_InputUtils-0.6.3\\plugins",
                "path_manifest": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\Rune580-LethalCompany_InputUtils-0.6.3\\manifest.json"
            },
            "x753-Mimics-2.4.1": {
                "path_.dll": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\x753-Mimics-2.4.1\\BepInEx\\plugins\\Mimics.dll",
                "path_bepinex": "C:Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\x753-Mimics-2.4.1\\BepInEx",
                "path_plugins": "C:Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\x753-Mimics-2.4.1\\BepInEx\\plugins",
                "path_manifest": "C:\\Users\\caram\\AppData\\Roaming\\space\\spaces\\TOBIMODS\\tests\\mods_test\\x753-Mimics-2.4.1\\manifest.json"
            }
        }
        for folder in folders:
            full_path = os.path.join(path, folder)
            files_rules.get_file_rules(full_path)

        self.assertDictEqual(expected_rules, files_rules.files_rules)

if __name__ == '__main__':
    unittest.main()

    
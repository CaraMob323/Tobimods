import unittest
import json
import os

from context import TobiMods

class TestGetVersion(unittest.TestCase):
    def test_get_local_version(self):
        local_version = TobiMods.GetLocalVersionManifest("tests\\mods_test", test_mode=True)
        version = local_version.get_version("BepInExPack")
        self.assertNotIsInstance(version, bool, "The version shoudnt be a BoolType") 
        self.assertEqual(version, "5.4.2100", f"The local version is not correct, {version}")

    def test_get_latest_version(self):
        latest_version = TobiMods.GetLatestVersionThunder()
        version, download_url = latest_version.get_version("x753", "Mimics")
        self.assertNotIsInstance(version, bool, "The version shoudnt be a Booltype")
        self.assertIsNotNone(version, "The version must not be a NoneType")

class TestGetModsInfo(unittest.TestCase):
    pass

class TestSearchMods(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.local_version = TobiMods.GetLocalVersionManifest("tests\\mods_test", test_mode=True)
        self.mod_info = TobiMods.GetModInfoYML()
        container = self.mod_info.get_container()
        self.latest_version = TobiMods.GetLatestVersionThunder(container)
        self.search_mods = TobiMods.SearchMods(self.local_version, self.latest_version)

    def test_is_outdated_mod(self):
        self.assertTrue(self.search_mods.is_outdated_mod("Diversity"), "This could be a outdated")
        self.assertFalse(self.search_mods.is_outdated_mod("BepInExPack"), "This couldnt be a outdated")

    def test_is_missing_mod(self):
        self.assertTrue(self.search_mods.is_missing_mod("Test"), "This mod must be missing")
        self.assertFalse(self.search_mods.is_missing_mod("Mimics"), "This mod shouldnt be a missing")
    
    def test_is_extra_mod(self):
        container = self.mod_info.get_container()
        self.assertTrue(self.search_mods.is_extra_mod("Test", container), "This mod must be a extra")
        self.assertFalse(self.search_mods.is_extra_mod("Mimics", container), "This mod shouldnt be a extra")
    


if __name__ == '__main__':
    unittest.main()




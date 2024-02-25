import unittest

from context import TobiMods

files_rules = TobiMods.core.GetFilesRules()
identify_mods = TobiMods.core.IdentifyMods()

class TestRules(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_rule_bepinex_plugins_dll(self):
        folder = TobiMods.core.diropenbox(title="Seleccione carpeta mods")
        files_rules.get_file_rules(folder)
        TobiMods.helpers.save_json(folder, "test_rules.json", files_rules.files_rules)

if __name__ == '__main__':
    unittest.main()
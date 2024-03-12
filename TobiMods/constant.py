from dataclasses import dataclass

@dataclass
class LethalConstant:
    BEPINEX_NAME = "BepInEx"
    PLUGINS_NAME = "plugins"
    CONFIG_NAME = "config"
    PATCHERS_NAME = "patchers"
    CORE_NAME = "core"

    YML_GITHUB_URL = "https://raw.githubusercontent.com/CaraMob323/Tobimods/main/mods.yml"
    YML_FILE_NAME = "mods.yml"
    YML_MOD_NAME = "displayName"
    YML_MOD_AUTHOR = "authorName"

    MANIFEST_FILE = "manifest.json"
    MANIFEST_MOD_NAME = "name"
    MANIFEST_MOD_AUTHOR = "author"
    MANIFEST_MOD_VERSION = "version_number"

    THUNDER_MOD_NAME = "name"
    THUNDER_MOD_VERSION = "version_number"
    THUNDER_LATEST = "latest"
    THUNDER_MOD_URL = "download_url"

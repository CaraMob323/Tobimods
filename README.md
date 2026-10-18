# TobiMods

[![GitHub release](https://img.shields.io/github/release/CaraMob323/tobimods)](https://github.com/CaraMob323/Tobimods/releases)

**Programa para Windows que deja la carpeta de tu juego con la misma lista de mods que el resto de tu grupo, con un solo clic.**

> **TobiMods no es un mod.** Es un programa externo (`.exe`) que descarga e instala mods de [Thunderstore](https://thunderstore.io) en tu juego. No agrega contenido ni cambia el juego por sí mismo.
>
> **Funciona con cualquier juego que use [BepInEx](https://github.com/BepInEx/BepInEx)** y cuyos mods estén publicados en Thunderstore. Solo su lista de mods por defecto es de Lethal Company (ver [Antes de ejecutarlo](#antes-de-ejecutarlo-ten-en-cuenta)).

---

## Qué hace

Al ejecutarlo, en este orden:

1. Te pide elegir la carpeta del juego: la que tiene el `.exe` del juego directamente adentro (por ejemplo, `Lethal Company.exe`).
2. Lee la lista de mods desde el archivo `mods.yml` que está junto al `.exe`. Si ese archivo no existe, descarga la lista del autor desde este repositorio (es una lista de **Lethal Company**, con 96 mods en la versión actual).
3. Busca los mods ya instalados en `BepInEx/plugins` (los identifica por su `manifest.json`).
4. Consulta en Thunderstore la **última versión** de cada mod de la lista.
5. Compara y clasifica cada mod:

   | Estado | Significa | Acción |
   |---|---|---|
   | `MISSING` | Está en la lista pero no en tu juego | Lo instala |
   | `OUTDATED` | Tu versión es distinta a la última de Thunderstore | Lo actualiza |
   | `EXTRA` | Está en tu juego pero no en la lista | Te pregunta si lo elimina |
   | *(sin mensaje)* | Está en la lista y en la última versión | No hace nada |

6. Instala y actualiza **sin pedir confirmación**.
7. Por cada mod `EXTRA`, pregunta: `¿Deseas eliminar este mod: <nombre> (y/n)?`

## Qué NO hace

- **No agrega ni modifica contenido del juego.** Solo instala mods de terceros.
- **No fija versiones.** Ignora la versión escrita en `mods.yml` y siempre instala la última de Thunderstore. Si dos jugadores lo ejecutan en días distintos y un mod se actualizó entre medio, pueden quedar con versiones distintas.
- **No resuelve dependencias.** Instala únicamente lo que figura en `mods.yml`. El `mods.yml` exportado por r2modman ya incluye las dependencias (incluido el paquete de BepInEx); si armas la lista a mano, agrégalas tú.
- **No instala BepInEx por separado.** El paquete de BepInEx de tu juego (por ejemplo, `BepInExPack` en Lethal Company) se trata como un mod más: tiene que estar en `mods.yml`.
- **No respeta `enabled: false`.** Todo lo que esté en la lista se instala.
- **No hace copias de seguridad** de tus mods, configuraciones ni archivos.
- **No sincroniza configuraciones entre jugadores.** Solo copia los archivos de configuración que traiga el propio paquete del mod (ver la advertencia más abajo).
- **No usa perfiles.** Instala directo en la carpeta del juego, no en un perfil de r2modman. r2modman no verá lo que instale TobiMods.
- **No verifica la integridad** de lo que descarga (sin hash ni firma). Los mods son código de terceros.
- **No inicia, cierra ni actualiza el juego.**
- **No instala mods que no estén en Thunderstore** (Nexus Mods, GitHub, archivos sueltos).
- **No funciona sin conexión a Internet.**
- **No funciona en otros sistemas operativos.** Solo Windows.

---

## Requisitos

- Windows.
- Un juego que use BepInEx y cuyos mods estén en Thunderstore (ejemplo de ruta, Lethal Company: `C:\Program Files (x86)\Steam\steamapps\common\Lethal Company`).
- Conexión a Internet.
- [r2modman](https://github.com/ebkr/r2modmanPlus/releases/latest), **solo** para quien arma la lista de mods.

## Uso

### 1. Quien arma la lista (una sola vez)

1. Instala r2modman, elige el juego y crea un perfil con todos los mods que quiere el grupo.
2. Abre la carpeta de ese perfil (desde r2modman, en *Settings → Locations*, o directamente en `%APPDATA%\r2modmanPlus-local\<NombreDelJuego>\profiles\<nombre-del-perfil>`; para Lethal Company, `<NombreDelJuego>` es `LethalCompany`).
3. Copia el archivo `mods.yml` de esa carpeta y compártelo con el grupo.

Si no usas r2modman, puedes escribir `mods.yml` a mano. De cada mod solo se leen dos campos, `displayName` y `authorName`:

```yaml
- displayName: Mimics
  authorName: x753
- displayName: MoreCompany
  authorName: notnotnotswipez
```

### 2. Cada jugador

1. **Cierra el juego.**
2. Descarga el `.exe` desde [Releases](https://github.com/CaraMob323/Tobimods/releases).
3. Coloca el `mods.yml` del grupo **en la misma carpeta que el `.exe`**.
4. Ejecuta el `.exe` con doble clic y elige la carpeta del juego.
5. Espera a que termine la instalación y responde las preguntas de eliminación.
6. Presiona Enter para cerrar.

---

## Antes de ejecutarlo, ten en cuenta

- **Sin `mods.yml` junto al `.exe`, se usa la lista del autor del proyecto**, que es de Lethal Company, no la tuya. Todo mod que tengas y no esté en esa lista aparecerá como `EXTRA`. Si usas otro juego, el programa intentará instalar esos mods de Lethal Company y te preguntará por borrar los tuyos. **Con cualquier otro juego, usa siempre tu propio `mods.yml`.**
- **En la pregunta de eliminación, solo `n` (minúscula) conserva el mod.** Cualquier otra respuesta —incluido Enter sin escribir nada, `N` o `no`— **lo elimina**.
- **Eliminar un mod borra únicamente su carpeta `BepInEx/plugins/<Autor>-<Mod>`.** No borra archivos que haya dejado en `BepInEx/config`, `core` o `patchers`.
- **Al actualizar, si el paquete del mod incluye un archivo de configuración, sobrescribe el que tengas** en `BepInEx/config` (se pierden tus ajustes en ese archivo). Haz una copia de esa carpeta si te importa.
- **Se usa una carpeta temporal `temp` dentro de la carpeta del juego** y se borra al terminar de instalar. Si ya tenías una carpeta con ese nombre ahí, también se borra.

## Cómo decide

- **Identificación:** compara el `displayName` de `mods.yml` con el `name` del `manifest.json` de cada mod instalado. El autor (`authorName`) se usa solo para consultar Thunderstore.
- **Versión:** compara por igualdad. Cualquier versión distinta a la última de Thunderstore cuenta como `OUTDATED`, incluso si la tuya es más nueva.
- **Instalación:** cada mod va a `BepInEx/plugins/<Autor>-<Mod>/`. Si el paquete trae carpetas `config`, `core` o `patchers` de BepInEx, esos archivos van a su carpeta correspondiente dentro de `BepInEx/`. Al actualizar, los archivos nuevos se copian encima de los existentes; los archivos de la versión anterior que ya no estén en la nueva **no se borran**.
- **Red:** solo hace peticiones de lectura (GET) a Thunderstore (API y descarga de mods) y, si no hay `mods.yml` local, a `raw.githubusercontent.com`. No envía datos de tu equipo.

## Limitaciones conocidas

- Si un mod de la lista ya no existe en Thunderstore (o no se pudo consultar), el programa se detiene con un error durante la instalación.
- Si la descarga de un mod responde con un error, reintenta sin límite hasta que responda bien.
- Si cancelas el diálogo de selección de carpeta al ejecutar el `.exe`, el programa termina con un error.

---

## Ejecutar desde el código fuente

Requiere Python 3.9 o superior (desarrollado con 3.12).

```
pip install requests aiohttp termcolor pyyaml easygui
python TobiMods/core.py
```

Ejecútalo desde la carpeta que contiene `mods.yml`: ahí busca la lista.

## Contribuir

Issues y pull requests son bienvenidos.

## Créditos

- [r2modman](https://github.com/ebkr/r2modmanPlus)
- [Thunderstore API](https://thunderstore.io/api/docs/)

## Licencia

[MIT](https://choosealicense.com/licenses/mit/) © 2024 Cara

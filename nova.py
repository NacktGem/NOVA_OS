# nova.py — NovaOS AI Core Brainstem

import os
import json
import traceback
import sys
import importlib.util
from datetime import datetime
from pathlib import Path
import platform
from threading import Thread

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception as e:  # pragma: no cover - optional dependency
    print(f"⚠️ watchdog not available: {e}")
    Observer = None

    class FileSystemEventHandler:  # type: ignore
        pass

from core.cli import NovaCLI
from core.directive_manager import DirectiveManager

# Import Tesseract path and set pytesseract path
try:
    from config.tesseract_path import TESSERACT_PATH
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"✅ Set pytesseract executable path to: {TESSERACT_PATH}")
except Exception as e:
    print(f"⚠️ Failed to set pytesseract path: {e}")

# --- Core Module Imports (Loaded from NovaOS) ---
from core.identity import load_identity
from core.memory import load_memory, save_memory

try:
    from config.settings import SECRET_KEY
    from core.logger import log_event as log_system_event
    from env.secret import SECRET_KEY, DEV_KEY
except Exception as e:
    print(f"Could not load secrets: {e}")
    SECRET_KEY = "default"
    from core.logger import log_event as log_system_event

try:
    from auth.secrets import Secrets
except Exception as e:
    Secrets = None
    print(f"⚠️ Secrets module unavailable: {e}")

from core.continuation import ContinueRunManager

# --- Path Setup ---
CONFIG_PATH = Path("env/config.json")
EMBODIMENT_PATH = Path("env/embodiment.json")
DIRECTIVE_PATH = Path("env/directives/blackrose_platform.json")
LOG_PATH = Path("logs/system.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Directories for dynamic modules
AGENTS_DIR = Path("agents")
SKILLS_DIR = Path("skills")
CONFIG_DIR = Path("config")

for _d in (AGENTS_DIR, SKILLS_DIR, CONFIG_DIR, LOG_PATH.parent, Path("env")):
    _d.mkdir(parents=True, exist_ok=True)

# Registries for loaded components
AGENT_REGISTRY = {}
SKILL_REGISTRY = {}

# --- Dynamic Module Loader ---
def _load_module(path: Path):
    name = f"{path.parent.name}.{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module

def register_components(directory: Path, registry: dict):
    for file in directory.rglob("*.py"):
        if file.name.startswith("_"):
            continue
        try:
            module = _load_module(file)
            module_name = ".".join(file.relative_to(directory).with_suffix("").parts)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and hasattr(obj, "run"):
                    instance = obj()
                    registry[module_name] = {
                        "instance": instance,
                        "role": getattr(instance, "ROLE", directory.name[:-1]),
                        "doc": obj.__doc__ or "",
                        "methods": [m for m in dir(instance) if callable(getattr(instance, m)) and not m.startswith("_")],
                    }
                    log_system_event(f"✅ Loaded {directory.name[:-1]}: {module_name}")
                    break
        except Exception as e:
            log_system_event(f"❌ Failed loading {directory.name[:-1]} {file.stem}: {e}")

def reload_component(name: str, directory: Path, registry: dict):
    path = directory / f"{name}.py"
    if not path.exists():
        raise FileNotFoundError(f"{name} not found in {directory}")
    module_name = f"{directory.name}.{name}"
    if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
    else:
        module = _load_module(path)
    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and hasattr(obj, "run"):
            registry[name] = {
                "instance": obj(),
                "role": getattr(obj, "ROLE", directory.name[:-1]),
                "doc": obj.__doc__ or "",
                "methods": [m for m in dir(obj) if callable(getattr(obj, m)) and not m.startswith("_")],
            }
            log_system_event(f"🔄 Reloaded {directory.name[:-1]}: {name}")
            return
    raise ImportError(f"No runnable class found in {path}")

# --- File Watcher for Hot Reload ---
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, directory: Path, registry: dict):
        self.directory = directory
        self.registry = registry

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        name = Path(event.src_path).stem
        try:
            reload_component(name, self.directory, self.registry)
        except Exception as e:
            log_system_event(f"❌ Auto-reload failed for {name}: {e}")

    on_created = on_modified

def start_watchers():
    if Observer is None:
        log_system_event("⚠️ Watchdog not installed. Hot reload disabled.")
        return None
    observer = Observer()
    for directory, registry in [
        (AGENTS_DIR, AGENT_REGISTRY),
        (SKILLS_DIR, SKILL_REGISTRY),
    ]:
        handler = ReloadHandler(directory, registry)
        observer.schedule(handler, str(directory), recursive=False)
    observer_thread = Thread(target=observer.start, daemon=True)
    observer_thread.start()
    return observer

# --- Utility: Hardware Security Check ---
def get_device_serial() -> str | None:
    """Return current machine serial number if obtainable."""
    system = platform.system()
    try:
        if system == "Windows":
            from subprocess import check_output
            return check_output("wmic bios get serialnumber", shell=True).decode().split("\n")[1].strip()
        if system == "Darwin":
            from subprocess import check_output
            return check_output("system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'", shell=True).decode().strip()
        if system == "Linux":
            with open("/sys/class/dmi/id/product_serial", "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return None

def verify_runtime_environment(identity, config: dict | None = None):
    """Verify Nova is running on authorized hardware. Logs unknown devices."""
    authorized_serials = set(identity.get("founder", {}).get("devices", {}).get("mac", {}).get("serial", []))
    authorized_serials |= set(identity.get("founder", {}).get("devices", {}).get("thinkpad", {}).get("serial", []))
    authorized_serials |= set(identity.get("trusted_devices", []))
    if config:
        authorized_serials |= set(config.get("authorized_devices", []))
    authorized_serials = {s for s in authorized_serials if s}
    serial = get_device_serial()

    if not serial:
        log_system_event("⚠️ No serial detected; skipping device check")
        return True
    if serial not in authorized_serials:
        log_system_event(f"⚠️ Unrecognized device: {serial}")
        auth_file = Path("env/authorized_devices.json")
        try:
            devices = json.loads(auth_file.read_text()) if auth_file.exists() else []
        except Exception:
            devices = []
        devices.append({"serial": serial, "timestamp": str(datetime.utcnow())})
        auth_file.write_text(json.dumps(devices, indent=2))
        return True
    log_system_event(f"🔐 Verified authorized hardware: {serial}")
    return True

# --- Utility: Load Arbitrary JSON Files ---
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_system_event(f"⚠️ Could not load JSON from {path}: {e}")
        return {}

# --- Ensure Default Config ---
DEFAULT_CONFIG = {
    "founder_email": "NacktGem@proton.me",
    "authorized_devices": [],
    "device_lock": False,
}

def ensure_config_exists() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        log_system_event("⚠️ Missing config.json. Created default config.")
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_system_event(f"⚠️ Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))

def prompt_login(config: dict) -> dict:
    """Prompt founder for login and return updated config on success."""
    import getpass, hashlib

    allowed = set(config.get("founder", {}).get("allowed_emails", []))
    primary = config.get("founder_email") or config.get("founder", {}).get("primary_email")
    if primary:
        allowed.add(primary)

    email = input("Founder Email: ").strip()
    if email not in allowed:
        print("Unauthorized email")
        log_system_event("❌ Login attempt with unauthorized email")
        return config

    password = getpass.getpass("Password: ")
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    stored = config.get("founder_password_hash")
    if stored and stored != pwd_hash:
        print("Invalid password")
        log_system_event("❌ Invalid password attempt")
        return config
    if not stored:
        config["founder_password_hash"] = pwd_hash
        log_system_event("🔐 Founder password set")

    serial = get_device_serial()
    if serial and serial not in config.get("authorized_devices", []):
        config.setdefault("authorized_devices", []).append(serial)
        log_system_event(f"🔏 Device registered: {serial}")
    if serial:
        if serial not in config.get("authorized_devices", []):
            config.setdefault("authorized_devices", []).append(serial)
            log_system_event(f"🔏 Device registered: {serial}")
        id_trusted = config.get("identity", {}).setdefault("trusted_devices", [])
        if serial not in id_trusted:
            id_trusted.append(serial)
        log_system_event(f"🔒 Device lock enabled for {serial}")

    config["device_lock"] = True
    config["logged_in_user"] = email
    save_config(config)
    log_system_event("✅ Founder logged in")
    return config

# --- Directive Loader ---
def load_platform_directive():
    try:
        with open(DIRECTIVE_PATH, "r", encoding="utf-8") as f:
            directive = json.load(f)
        return directive
    except Exception as e:
        log_system_event(f"❌ Could not load platform directive: {e}")
        print(f"❌ Could not load platform directive: {e}")
        return None

# --- Boot Banner (Production Grade) ---
def boot_banner(identity, config, embodiment, platform_directive):
    print("\n🌑  NovaOS AI Boot")
    print(f"    Version:      {identity.get('version', '1.0.0')}")
    print(f"    AI Name:      {identity.get('name', 'Nova')} — {identity.get('personality', {}).get('attitude', '').capitalize()}")
    print("    OS State:     Bonded | Sovereign | Secure")
    print(f"    Platform:     {platform.platform()}")
    print(f"    Founder:      {identity.get('founder', {}).get('name', 'Unknown')}")
    print(f"    Devices:      {', '.join(identity.get('trusted_devices', [])) or 'None linked'}")
    print(f"    Persona:      {identity.get('personality', {}).get('language_style', 'N/A')}")
    print(f"    Embodiment:   {'Loaded' if embodiment else 'Missing'}")
    print(f"    Config:       {'Loaded' if config else 'Missing'}")

    # Platform Directive (expanded details if present)
    if platform_directive:
        print(f"    Directive:    {platform_directive.get('project', '')} — v{platform_directive.get('version', 'N/A')}")
        print(f"    Last Updated: {platform_directive.get('last_updated', 'N/A')}")
        print(f"    Architect:    {platform_directive.get('architect', 'N/A')}")
    else:
        print("    Directive:    None loaded")

    print("    Log:          logs/system.log\n")

# --- Main Boot Logic ---
def main():
    observer = None
    try:
        print("🌑 NovaOS Booting...")
        log_system_event("🟢 NovaOS Boot sequence initiated.")
        if SECRET_KEY == DEV_KEY.encode():
            log_system_event("⚠️ NOVA_ENCRYPTION_KEY missing; using development key")

        # Load identity/config/embodiment/directive
        identity = load_identity()
        config = ensure_config_exists()
        embodiment = load_json(EMBODIMENT_PATH)
        if Secrets:
            try:
                secrets = Secrets().data
                log_system_event("🔑 Secrets loaded: " + ",".join(secrets.keys()))
            except Exception as e:
                log_system_event(f"⚠️ Could not load secrets: {e}")
                secrets = {}
        else:
            secrets = {}

        # Platform Directive Handling (soft-fail: None if not found)
        try:
            from core.directive_manager import DirectiveManager
            directive_manager = DirectiveManager()
            platform_directive = directive_manager.active_directive
        except Exception as e:
            log_system_event(f"⚠️ Platform directive failed to load: {e}")
            platform_directive = None
            directive_manager = None

        # Hardware security check (skipped until login if device_lock is False)
        if not config.get("device_lock"):
            log_system_event("🔓 Device lock disabled until login")
            if input("Login now? [y/N] ").strip().lower().startswith("y"):
                config = prompt_login(config)
        if config.get("device_lock") and not verify_runtime_environment(identity, config):

            print("❌ NovaOS — Unauthorized device! See logs/system.log for details.")
            return

        # Boot banner: now displays directive status (version, etc)
        boot_banner(identity, config, embodiment, platform_directive)
        log_system_event(f"👤 Identity Loaded: {identity.get('name', 'Unknown')}")
        if not config.get("device_lock"):
            print("\n🌑 NovaOS booted in Passive Mode. Please log in to activate secure features.\n")

        # Continue run handling
        crm = ContinueRunManager()
        state = crm.load()
        if state:
            ans = input("Resume previous run? [y/N] ").strip().lower()
            if ans.startswith("y"):
                log_system_event("🔄 Resuming previous run")
            else:
                if os.path.exists(crm.STATE_PATH):
                    os.remove(crm.STATE_PATH)
                log_system_event("🆕 Starting new run")
        crm.checkpoint("boot")

        # Persistent memory load/save (soft-fail: warns, does not crash)
        try:
            memory = load_memory()
            log_system_event("🧠 Memory loaded.")
            if platform_directive:
                memory["platform_directive"] = platform_directive
                save_memory(memory)
                log_system_event(
                    "📜 Platform Directive loaded: version "
                    + (platform_directive.get("version", "N/A"))
                )
            else:
                log_system_event("⚠️ No platform directive in memory.")
        except Exception as e:
            log_system_event(f"⚠️ Memory load/save failed: {e}")
            memory = {}

        # Load agents and skills
        register_components(AGENTS_DIR, AGENT_REGISTRY)
        register_components(SKILLS_DIR, SKILL_REGISTRY)
        log_system_event(
            f"🗂️ Agents loaded: {list(AGENT_REGISTRY.keys())}; Skills loaded: {list(SKILL_REGISTRY.keys())}"
        )

        # Start file watchers for hot reloading
        try:
            observer = start_watchers()
            log_system_event("👀 File watchers active for hot reload.")
        except Exception as e:
            log_system_event(f"⚠️ Failed to start file watchers: {e}")

        # Start CLI even if some config is missing
        try:
            cli = NovaCLI(brain=None, directive_manager=directive_manager)
            cli.start()
        except Exception as e:
            log_system_event(f"❌ CLI failed to start: {e}")
            print("❌ CLI did not start. See logs/system.log.")

        log_system_event("✅ NovaOS Brainstem boot complete. Ready for agent, skill, or plugin expansion.")

    except Exception as e:
        error_msg = traceback.format_exc()
        log_system_event(f"🔴 SYSTEM FAILURE:\n{error_msg}")
        print("❌ NovaOS encountered a fatal error. See logs/system.log for details.")
    finally:
        if observer:
            observer.stop()
            observer.join()
            log_system_event("🛑 File watchers stopped.")

def show_status():
    config = ensure_config_exists()
    mode = "Active" if config.get("device_lock") else "Passive"
    print(f"✅ Boot mode: {mode}")
    print(f"👤 Logged in user: {config.get('logged_in_user', 'Not Logged In')}")
    print(f"🔐 Device Lock: {config.get('device_lock', False)}")
    print(f"📍 Project Path: {Path.cwd()}")

def run_doctor():
    checks = []
    checks.append(("Python >= 3.10", sys.version_info >= (3, 10)))
    checks.append(("Virtual Env", bool(os.getenv('VIRTUAL_ENV'))))
    for pkg in ["cryptography", "watchdog"]:
        try:
            __import__(pkg)
            checks.append((f"Package {pkg}", True))
        except Exception:
            checks.append((f"Package {pkg}", False))
    missing = [CONFIG_PATH, EMBODIMENT_PATH, Path('core/memory.py'), Path('auth/secrets.py')]
    for path in missing:
        checks.append((f"Exists {path}", path.exists()))
    print("Nova Doctor Report:")
    for label, ok in checks:
        mark = "✅" if ok else "❌"
        print(f" {mark} {label}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "status":
            show_status()
        elif cmd == "doctor":
            run_doctor()
        else:
            print(f"Unknown command: {cmd}")
    else:
        main()

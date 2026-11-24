#!/usr/bin/env python3
import argparse
import getpass
import os
import re
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULES = ("common", "fabric", "forge", "neoforge")
PLATFORMS = ("fabric", "forge", "neoforge")
TEXT_EXTENSIONS = {".java", ".json", ".toml", ".gradle", ".properties", ".accesswidener", ".cfg", ".md"}
SKIPPED_DIRS = {".git", ".gradle", ".idea", "build", "run", "out", "bin"}
SECRETS = (
    ("GITHUB_TOKEN", "GitHub token (releases)"),
    ("MODRINTH_TOKEN", "Modrinth token"),
    ("CURSEFORGE_TOKEN", "CurseForge API token"),
    ("CURSEFORGE_SESSION_COOKIE", "CurseForge CobaltSession cookie (README sync)"),
    ("CURSEFORGE_AUTHORS_USER", "CurseForge AuthorsUser cookie (README sync)"),
)

MOD_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
GROUP_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$")


def version_key(version):
    return [int(part) for part in re.findall(r"\d+", version)]


def read_properties(path):
    properties = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            properties[key.strip()] = value.strip()
    return properties


def update_properties(path, values):
    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)
        replacement = f"{key} = {value}"
        if pattern.search(text):
            text = pattern.sub(lambda _: replacement, text)
        else:
            text = text.rstrip("\n") + f"\n{replacement}\n"
    path.write_text(text, encoding="utf-8")


def read_dotenv(path):
    values = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
            if match:
                values[match.group(1)] = match.group(2).strip("'\"")
    return values


def write_dotenv(path, values):
    lines = [f"{key}={value}" for key, value in values.items() if value]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


class Prompter:
    def __init__(self, assume_defaults):
        self.assume_defaults = assume_defaults

    def text(self, label, default, validate=None, error=None):
        while True:
            if self.assume_defaults:
                value = default
            else:
                raw = input(f"{label} [{default}]: ").strip()
                value = raw or default
            if validate is None or validate(value):
                return value
            if self.assume_defaults:
                sys.exit(f"Invalid value for {label}: {value!r}. {error or ''}")
            print(error or "Invalid value, try again.")

    def choice(self, label, options, default):
        options = list(options)
        return self.text(f"{label} ({'/'.join(options)})", default, lambda v: v in options, f"Choose one of: {', '.join(options)}")

    def multi_choice(self, label, options, default):
        options = list(options)

        def valid(value):
            items = [item.strip() for item in value.split(",") if item.strip()]
            return bool(items) and all(item in options for item in items)

        value = self.text(f"{label} ({','.join(options)})", ",".join(default), valid, f"Comma separated, from: {', '.join(options)}")
        return [item.strip() for item in value.split(",") if item.strip()]

    def yes_no(self, label, default):
        value = self.text(f"{label} (y/n)", "y" if default else "n", lambda v: v.lower() in ("y", "yes", "n", "no"))
        return value.lower() in ("y", "yes")

    def secret(self, label, current):
        if self.assume_defaults:
            return current
        hint = "keep current, '-' to clear" if current else "leave empty to skip"
        value = getpass.getpass(f"{label} ({hint}): ").strip()
        if value == "-":
            return ""
        return value or current


def iter_files(base):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        for name in files:
            yield Path(root) / name


def java_roots(module_dir):
    roots = [module_dir / "src" / "main" / "java"]
    variants = module_dir / "src" / "variants"
    if variants.is_dir():
        roots += [variant / "java" for variant in sorted(variants.iterdir()) if (variant / "java").is_dir()]
    return [root for root in roots if root.is_dir()]


def remove_empty_parents(path, stop):
    path = path.parent
    while path != stop and path.is_dir() and not any(path.iterdir()):
        path.rmdir()
        path = path.parent


def move_package(old_package, new_package):
    if old_package == new_package:
        return
    for module in MODULES:
        for root in java_roots(ROOT / module):
            old_dir = root.joinpath(*old_package.split("."))
            new_dir = root.joinpath(*new_package.split("."))
            if not old_dir.is_dir():
                continue
            new_dir.mkdir(parents=True, exist_ok=True)
            for item in list(old_dir.iterdir()):
                shutil.move(str(item), str(new_dir / item.name))
            old_dir.rmdir()
            remove_empty_parents(old_dir, root)


def replace_in_files(replacements):
    for path in iter_files(ROOT):
        if path.suffix not in TEXT_EXTENSIONS or path.name in ("gradle.properties", "CHANGELOG.md"):
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def rename_paths(old_id, new_id):
    if old_id == new_id:
        return
    candidates = [p for p in ROOT.rglob(f"*{old_id}*") if not (set(p.relative_to(ROOT).parts) & SKIPPED_DIRS)]
    for path in sorted(candidates, key=lambda p: len(p.parts), reverse=True):
        if path.exists():
            path.rename(path.with_name(path.name.replace(old_id, new_id)))


def set_java_constant(name, value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    for path in (ROOT / "common" / "src" / "main" / "java").rglob("Main.java"):
        text = path.read_text(encoding="utf-8")
        text = re.sub(rf'(public static final String {name} = )".*?";', lambda m: f'{m.group(1)}"{escaped}";', text)
        path.write_text(text, encoding="utf-8")


def flatten_sources(version_file, platforms):
    properties = read_properties(version_file)
    for module in MODULES:
        module_dir = ROOT / module
        variants_dir = module_dir / "src" / "variants"
        if not variants_dir.is_dir():
            continue
        variant = properties.get(f"{module}_sources")
        if variant and (module == "common" or module in platforms):
            for kind in ("java", "resources"):
                source = variants_dir / variant / kind
                if source.is_dir():
                    shutil.copytree(source, module_dir / "src" / "main" / kind, dirs_exist_ok=True)
        shutil.rmtree(variants_dir)


def prune_version_file(version_file, platforms):
    removed = [p for p in PLATFORMS if p not in platforms]
    removed_keys = [f"{p}_" for p in removed] + (["mod_menu_version"] if "fabric" in removed else [])
    removed_headers = {"# Source variants"} | {f"# {name}" for p, name in
                                               (("fabric", "Fabric"), ("forge", "Forge"), ("neoforge", "NeoForge")) if p in removed}

    sections = version_file.read_text(encoding="utf-8").strip().split("\n\n")
    kept = []
    for section in sections:
        lines = section.splitlines()
        if lines and lines[0] in removed_headers:
            continue
        lines = [line for line in lines
                 if not re.match(r"^[a-z]+_sources\s*=", line) and not any(line.startswith(key) for key in removed_keys)]
        lines = [f"supported_loaders = {','.join(platforms)}" if line.startswith("supported_loaders") else line for line in lines]
        if any(not line.startswith("#") for line in lines):
            kept.append("\n".join(lines))
    version_file.write_text("\n\n".join(kept) + "\n", encoding="utf-8")


def remove_unused_metadata(version_file):
    neoforge_version = read_properties(version_file).get("neoforge_version", "")
    meta_dir = ROOT / "neoforge" / "src" / "main" / "resources" / "META-INF"
    if neoforge_version and meta_dir.is_dir():
        legacy = re.match(r"^20\.[234]\.", neoforge_version) is not None
        unused = meta_dir / ("neoforge.mods.toml" if legacy else "mods.toml")
        if unused.exists():
            unused.unlink()
            return unused.relative_to(ROOT).as_posix()
    return None


def remove_other_versions(keep):
    for path in (ROOT / "versions").glob("*.properties"):
        if path.name != keep.name:
            path.unlink()


def ignore_in_template_updates(patterns):
    ignore_file = ROOT / ".templateignore"
    existing = ignore_file.read_text(encoding="utf-8").splitlines() if ignore_file.exists() else []
    added = [pattern for pattern in patterns if pattern not in existing]
    if added:
        ignore_file.write_text("\n".join(existing + added) + "\n", encoding="utf-8")


def remove_platform_modules(platforms):
    for platform in PLATFORMS:
        if platform not in platforms and (ROOT / platform).is_dir():
            shutil.rmtree(ROOT / platform)


def parse_args():
    parser = argparse.ArgumentParser(description="Configure this Architectury mod template.")
    parser.add_argument("--mod-id")
    parser.add_argument("--mod-name")
    parser.add_argument("--group", help="Maven group, the Java package becomes <group>.<mod id>")
    parser.add_argument("--author")
    parser.add_argument("--description")
    parser.add_argument("--license")
    parser.add_argument("--sources", help="Source code URL")
    parser.add_argument("--mod-version")
    parser.add_argument("--environment", choices=("client", "server", "both"))
    parser.add_argument("--minecraft", help="Target Minecraft version")
    parser.add_argument("--platforms", help="Comma separated platforms")
    parser.add_argument("--architectury-api", choices=("y", "n"))
    parser.add_argument("--repo-owner")
    parser.add_argument("--repo-name")
    parser.add_argument("--repo-branch")
    parser.add_argument("--modrinth-id")
    parser.add_argument("--curseforge-id")
    parser.add_argument("--release-type", choices=("release", "beta", "alpha"))
    parser.add_argument("--single-version", choices=("y", "n"), help="Keep only the selected Minecraft version")
    parser.add_argument("--skip-secrets", action="store_true", help="Don't ask for publishing tokens")
    parser.add_argument("-y", "--yes", action="store_true", help="Accept defaults for everything not given")
    return parser.parse_args()


def main():
    args = parse_args()
    prompt = Prompter(args.yes)

    gradle_properties = ROOT / "gradle.properties"
    current = read_properties(gradle_properties)
    old_id = current["mod_id"]
    old_group = current["maven_group"]

    versions = sorted((p.stem for p in (ROOT / "versions").glob("*.properties")), key=version_key)
    if not versions:
        sys.exit("No version profiles found in versions/")

    print("Architectury Template setup\n")

    mod_id = args.mod_id or prompt.text("Mod ID", old_id, MOD_ID_PATTERN.match, "Lowercase letters, digits and underscores, starting with a letter.")
    mod_name = args.mod_name or prompt.text("Mod name", current["mod_name"])
    group = args.group or prompt.text("Maven group", old_group, GROUP_PATTERN.match, "Use a lowercase Java package, e.g. io.github.me")
    author = args.author or prompt.text("Author", current["mod_author"])
    description = args.description or prompt.text("Description", current["mod_description"])
    license_name = args.license or prompt.text("License", current["mod_license"])
    mod_version = args.mod_version or prompt.text("Mod version", current["mod_version"])
    environment = args.environment or prompt.choice("Environment", ("client", "server", "both"), current.get("mod_environment", "client"))

    default_version = current.get("target_minecraft_version") if current.get("target_minecraft_version") in versions else versions[-1]
    if not args.minecraft and not args.yes:
        print(f"Available Minecraft versions: {', '.join(versions)}")
    minecraft = args.minecraft or prompt.text("Minecraft version", default_version, lambda v: v in versions, "Pick one of the listed versions.")

    version_file = ROOT / "versions" / f"{minecraft}.properties"
    version_properties = read_properties(version_file)
    supported = [p.strip() for p in version_properties["supported_loaders"].split(",")]
    current_platforms = [p.strip() for p in current.get("enabled_platforms", "").split(",") if p.strip() in supported] or supported
    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
        unsupported = [p for p in platforms if p not in supported]
        if unsupported:
            sys.exit(f"Minecraft {minecraft} doesn't support {', '.join(unsupported)} (supported: {', '.join(supported)})")
    else:
        platforms = prompt.multi_choice("Platforms", supported, current_platforms)

    architectury_api = current.get("include_architectury_api", "false") == "true"
    if args.architectury_api:
        architectury_api = args.architectury_api == "y"
    elif "architectury_api_version" in version_properties:
        architectury_api = prompt.yes_no("Depend on Architectury API", architectury_api)
    else:
        architectury_api = False

    repo_owner = args.repo_owner or prompt.text("GitHub owner", current["repo_owner"])
    repo_name = args.repo_name or prompt.text("GitHub repository", current["repo_name"] if current["repo_name"] != old_id else mod_id)
    repo_branch = args.repo_branch or prompt.text("Release branch", current["repo_branch"])
    default_sources = current["mod_sources"]
    if "github.com/Me/" in default_sources:
        default_sources = f"https://github.com/{repo_owner}/{repo_name}"
    sources = args.sources or prompt.text("Sources URL", default_sources)
    modrinth_id = args.modrinth_id or prompt.text("Modrinth project ID", current["modrinth_id"])
    curseforge_id = args.curseforge_id or prompt.text("CurseForge project ID", current["curseforge_id"], str.isdigit, "CurseForge project IDs are numeric.")
    release_type = args.release_type or prompt.choice("Release type", ("release", "beta", "alpha"), current.get("release_type", "release"))

    has_variants = any((ROOT / module / "src" / "variants").is_dir() for module in MODULES)
    single_version = False
    if has_variants:
        if args.single_version:
            single_version = args.single_version == "y"
        else:
            single_version = prompt.yes_no(f"Only keep Minecraft {minecraft} (removes other version profiles and source variants)", False)

    secrets = read_dotenv(ROOT / ".env")
    if not args.skip_secrets and not args.yes:
        print("\nPublishing credentials are stored in .env (git ignored). Environment variables take precedence.")
        for key, label in SECRETS:
            secrets[key] = prompt.secret(label, secrets.get(key, ""))

    print("\nApplying changes...")

    old_package = f"{old_group}.{old_id}"
    new_package = f"{group}.{mod_id}"
    move_package(old_package, new_package)
    replace_in_files([(old_package, new_package), (old_id, mod_id)])
    rename_paths(old_id, mod_id)
    set_java_constant("MOD_ID", mod_id)
    set_java_constant("MOD_NAME", mod_name)

    update_properties(gradle_properties, {
        "mod_id": mod_id,
        "mod_name": mod_name,
        "mod_description": description,
        "mod_author": author,
        "mod_sources": sources,
        "mod_license": license_name,
        "mod_version": mod_version,
        "mod_environment": environment,
        "maven_group": group,
        "archives_name": mod_id,
        "target_minecraft_version": minecraft,
        "enabled_platforms": ",".join(platforms),
        "include_architectury_api": str(architectury_api).lower(),
        "release_type": release_type,
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "repo_branch": repo_branch,
        "modrinth_id": modrinth_id,
        "curseforge_id": curseforge_id,
    })

    if single_version:
        flatten_sources(version_file, platforms)
        removed_metadata = remove_unused_metadata(version_file)
        prune_version_file(version_file, platforms)
        remove_other_versions(version_file)
        remove_platform_modules(platforms)
        ignore_in_template_updates(["versions/**"] + ([removed_metadata] if removed_metadata else [])
                                   + [f"{platform}/**" for platform in PLATFORMS if platform not in platforms])

    if any(secrets.values()):
        write_dotenv(ROOT / ".env", secrets)

    print(f"\nDone. Package: {new_package}, Minecraft {minecraft}, platforms: {', '.join(platforms)}")
    print("Build with ./gradlew build, or change target_minecraft_version in gradle.properties.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nAborted.")

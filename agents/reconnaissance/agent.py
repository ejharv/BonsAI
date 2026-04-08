"""
The reconnaissance agent is the first agent to run on any brownfield project.
It reads the existing codebase, integrates graphify output if available,
identifies domain boundaries, detects patterns, surfaces gaps, and produces
a ReconnaissanceOutput that drives roster creation and root population.

It is read-only with respect to the project codebase. It never modifies
source files. It only writes to roots/ via RootManager.
"""

from __future__ import annotations
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Optional

from root_manager.manager import RootManager
from root_manager.models import (
    CodebaseEntry,
    DependencyEntry,
    ProjectState,
)
from agents.reconnaissance.models import (
    ReconnaissanceInput,
    ReconnaissanceOutput,
    ObservedDomain,
    DetectedPattern,
    DeveloperGap,
    ConfidenceLevel,
    GapSeverity,
)


def today_iso() -> str:
    """Return today's date as ISO format string YYYY-MM-DD."""
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# Directories to skip entirely during tree walk
_EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "eggs",
}

# Folder names that are never domains (support/meta folders)
_NON_DOMAIN_FOLDERS = {
    "tests", "test", "__tests__", "docs", "documentation",
    "scripts", "tools", "bin", "assets", "static", "public",
    "node_modules", ".git",
}

# Top-level folders that contain domain subdirectories rather than being
# domains themselves. e.g. "src/auth/" means auth is the domain, not src.
_CONTAINER_FOLDERS = {"src", "app", "lib", "packages", "services", "modules"}

_CONFIG_FILES = {
    "package.json", "pyproject.toml", "setup.py", "setup.cfg",
    "requirements.txt", "Cargo.toml", "go.mod", "pom.xml",
    "build.gradle", "Makefile", "docker-compose.yml", "Dockerfile",
    ".env.example", "tsconfig.json", "webpack.config.js",
    "vite.config.ts", "vite.config.js",
}

_ENTRY_POINTS = {
    "main.py", "app.py", "index.py", "server.py", "manage.py",
    "index.ts", "index.js", "main.ts", "main.js", "App.tsx",
    "App.jsx", "app.ts", "app.js",
}

# Filenames that appear in many folders by convention — not duplication
_CONVENTIONAL_FILENAMES = {
    "__init__.py", "index.py", "index.ts", "index.js",
    "README.md", "types.py", "types.ts", "models.py",
}

# Package name -> domain hint (requirements.txt signal)
_PACKAGE_DOMAIN_HINTS = {
    "django": "web", "flask": "web", "fastapi": "api", "starlette": "api",
    "sqlalchemy": "database", "pymongo": "database", "redis": "cache",
    "celery": "tasks", "jwt": "auth", "bcrypt": "auth", "authlib": "auth",
    "boto3": "cloud", "stripe": "payments", "sendgrid": "email",
    "pytest": "testing", "numpy": "data", "pandas": "data",
    "tensorflow": "ml", "torch": "ml", "sklearn": "ml",
}

# Domain name -> one-sentence purpose description
_KNOWN_PURPOSES = {
    "auth": "Handles user authentication and session management",
    "authentication": "Handles user authentication and session management",
    "api": "Provides HTTP API endpoints and request handling",
    "web": "Serves web framework routes and views",
    "database": "Manages data persistence and database access",
    "db": "Manages data persistence and database access",
    "cache": "Provides caching layer for performance optimization",
    "tasks": "Handles background task processing and job queues",
    "ml": "Machine learning model training and inference",
    "data": "Data processing, analysis, and transformation",
    "payments": "Handles payment processing and billing",
    "email": "Manages email delivery and templates",
    "cloud": "Cloud infrastructure and deployment utilities",
    "testing": "Test utilities and test infrastructure",
    "utils": "Shared utilities and helper functions",
    "core": "Core business logic and domain primitives",
    "common": "Shared components and utilities",
    "shared": "Shared components used across multiple domains",
    "services": "Business service layer",
    "models": "Data models and schema definitions",
    "cli": "Command-line interface and developer tooling",
    "config": "Configuration management and environment handling",
    "middleware": "Request/response middleware pipeline",
}


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _normalize_name(name: str) -> str:
    """Normalize a name to lowercase with underscores."""
    return name.lower().replace("-", "_").replace(" ", "_")


def _derive_purpose(name: str, evidence: list[str], structure: dict) -> str:
    """
    Derive a one-sentence purpose from the domain name and evidence signals.
    Falls back to 'Purpose unclear' if no known mapping exists.
    """
    if name in _KNOWN_PURPOSES:
        return _KNOWN_PURPOSES[name]
    # Prefix/suffix match for compound names like "user_auth" or "auth_service"
    for key, purpose in _KNOWN_PURPOSES.items():
        if name.startswith(key) or name.endswith(key):
            return purpose
    return "Purpose unclear — requires developer input"


def _find_cross_domain_deps(
    project_path: Path,
    files: list[str],
    all_domain_names: set[str],
) -> list[str]:
    """
    Scan Python and JS/TS import statements in the given files for references
    to other known domain folder names. Returns list of domain names imported.
    This is a heuristic — it catches obvious cross-domain imports only.
    """
    deps: set[str] = set()
    py_pattern = re.compile(r"^\s*(?:import|from)\s+([\w.]+)", re.MULTILINE)
    js_pattern = re.compile(
        r'(?:import|require)\s*\(?["\']([^"\']+)["\']', re.MULTILINE
    )

    for file_str in files:
        file_path = project_path / file_str
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        suffix = file_path.suffix.lower()
        if suffix == ".py":
            for match in py_pattern.finditer(content):
                module = match.group(1).split(".")[0]
                if module in all_domain_names:
                    deps.add(module)
        elif suffix in (".ts", ".tsx", ".js", ".jsx"):
            for match in js_pattern.finditer(content):
                import_path = match.group(1)
                for domain in all_domain_names:
                    if domain in import_path:
                        deps.add(domain)

    return list(deps)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class ReconnaissanceAgent:
    """
    Reads an existing codebase and produces a structured understanding
    of its domain boundaries, patterns, and gaps.

    Never modifies source files.
    Writes only to roots/ via RootManager.
    Asks developer only what it cannot determine from the codebase itself.
    """

    def __init__(
        self,
        root_manager: RootManager,
        project_path: Path,
    ):
        """
        root_manager: initialized RootManager pointed at the project's roots/
        project_path: absolute path to the project root
        """
        self.root_manager = root_manager
        self.project_path = project_path
        self._graphify_data: dict = {}
        self._structure: dict = {}
        self._git_signals: dict = {}
        # Stored during run() so identify_gaps can filter by involvement level
        self._involvement_preference: str = "high"

    def run(
        self,
        input: ReconnaissanceInput,
    ) -> ReconnaissanceOutput:
        """
        Main entry point. Runs the full reconnaissance pipeline in order.
        Never raises — catches all errors and returns output with
        ready_to_proceed=False and the error in confidence_summary.
        """
        try:
            self._involvement_preference = input.involvement_preference

            # Step 1
            self.root_manager.begin_session("reconnaissance")

            # Step 2
            if input.use_graphify and input.graphify_report_path:
                self._graphify_data = self.load_graphify_report(
                    Path(input.graphify_report_path)
                )

            # Step 3
            self._structure = self.scan_project_structure()

            # Step 4
            domains = self.identify_domains(self._structure, self._graphify_data)

            # Step 5
            patterns = self.detect_patterns(self._structure)

            # Step 6
            if input.trust_git_history:
                self._git_signals = self.analyze_git_history()

            # Step 7
            gaps = self.identify_gaps(domains, self._structure)

            # Step 8
            roster = self.propose_roster(domains)

            # Step 9
            output = ReconnaissanceOutput(
                observed_domains=domains,
                detected_patterns=patterns,
                developer_gaps=gaps,
                proposed_roster=roster,
                health_observations=self._extract_health(patterns),
                confidence_summary=self._build_summary(domains, gaps),
                ready_to_proceed=not any(
                    g.severity == GapSeverity.BLOCKING for g in gaps
                ),
            )

            # Step 10
            self.write_to_roots(output)

            # Step 11
            self.root_manager.end_session(
                "reconnaissance",
                (
                    f"Reconnaissance complete. {len(domains)} domains found. "
                    f"{len(gaps)} gaps identified. "
                    f"Ready: {output.ready_to_proceed}"
                ),
            )

            # Step 12
            return output

        except Exception as exc:
            return ReconnaissanceOutput(
                observed_domains=[],
                detected_patterns=[],
                developer_gaps=[],
                proposed_roster=[],
                health_observations=[],
                confidence_summary=str(exc),
                ready_to_proceed=False,
            )

    def _extract_health(
        self,
        patterns: list[DetectedPattern],
    ) -> list[str]:
        """
        Return plain english health observations for patterns marked as repetitions.
        """
        result = []
        for p in patterns:
            if p.is_repetition:
                locations_str = ", ".join(p.locations)
                result.append(
                    f"Repeated pattern detected: {p.name} appears "
                    f"{p.instance_count} times across {locations_str}"
                )
        return result

    def _build_summary(
        self,
        domains: list[ObservedDomain],
        gaps: list[DeveloperGap],
    ) -> str:
        """
        Return a plain english paragraph summarising confidence and gaps.
        """
        high = sum(1 for d in domains if d.confidence == ConfidenceLevel.HIGH)
        medium = sum(1 for d in domains if d.confidence == ConfidenceLevel.MEDIUM)
        low = sum(1 for d in domains if d.confidence == ConfidenceLevel.LOW)
        blocking = sum(1 for g in gaps if g.severity == GapSeverity.BLOCKING)

        domain_word = "domain" if len(domains) == 1 else "domains"
        parts = [
            f"Found {len(domains)} {domain_word}: "
            f"{high} with high confidence, {medium} medium, {low} low."
        ]

        if gaps:
            gap_word = "gap" if len(gaps) == 1 else "gaps"
            parts.append(
                f"{len(gaps)} {gap_word} identified, {blocking} blocking."
            )
        else:
            parts.append("No gaps identified.")

        if blocking > 0:
            parts.append("Cannot proceed until the blocking gap is resolved.")

        return " ".join(parts)

    def load_graphify_report(
        self,
        report_path: Path,
    ) -> dict:
        """
        Read and parse GRAPH_REPORT.md produced by graphify.
        Returns dict with keys: god_nodes, communities, connections, raw.
        Returns empty dict and logs warning if file not found.
        If sections are missing returns dict with empty lists and raw content.
        """
        if not report_path.exists():
            print(f"Warning: graphify report not found at {report_path}")
            return {}

        try:
            raw = report_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Warning: could not read graphify report: {exc}")
            return {}

        god_nodes: list[str] = []
        communities: list[str] = []
        connections: list[str] = []
        current_section = ""

        for line in raw.splitlines():
            stripped = line.strip()

            # Detect section headings — stop accumulating on any new heading
            if re.match(r"^#{1,3}\s+God\s+Nodes", stripped, re.IGNORECASE):
                current_section = "god_nodes"
                continue
            elif re.match(r"^#{1,3}\s+Communities", stripped, re.IGNORECASE):
                current_section = "communities"
                continue
            elif re.match(
                r"^#{1,3}\s+(Surprising|Connections)", stripped, re.IGNORECASE
            ):
                current_section = "connections"
                continue
            elif re.match(r"^#{1,3}\s+", stripped):
                # Any other heading ends the current tracked section
                current_section = ""
                continue

            if not stripped:
                continue

            if current_section == "god_nodes":
                god_nodes.append(stripped)
            elif current_section == "communities":
                communities.append(stripped)
            elif current_section == "connections":
                connections.append(stripped)

        return {
            "god_nodes": god_nodes,
            "communities": communities,
            "connections": connections,
            "raw": raw,
        }

    def scan_project_structure(
        self,
    ) -> dict:
        """
        Walk the project directory tree using os.walk with pruning.
        Collects folder structure, file extensions, config files, entry points,
        and manifest contents. Never reads beyond config and manifest files.
        """
        folders: list[str] = []
        files_by_extension: dict[str, list[str]] = defaultdict(list)
        config_files: list[str] = []
        entry_points: list[str] = []
        manifest_contents: dict = {}
        top_level_folders: list[str] = []

        project_root = self.project_path

        for dirpath, dirnames, filenames in os.walk(project_root, topdown=True):
            current = Path(dirpath)
            try:
                rel_dir = current.relative_to(project_root)
            except ValueError:
                continue

            rel_parts = rel_dir.parts

            # Prune excluded directories in-place so os.walk skips them
            dirnames[:] = [
                d for d in dirnames
                if d not in _EXCLUDED_DIRS and not d.endswith(".egg-info")
            ]

            # Record top-level folders (depth == 1)
            if len(rel_parts) == 1:
                top_level_folders.append(rel_dir.name)

            # Record directory (skip the project root itself)
            if rel_parts:
                folders.append(str(rel_dir))

            for filename in filenames:
                file_path = current / filename
                try:
                    rel_file = file_path.relative_to(project_root)
                except ValueError:
                    continue
                rel_str = str(rel_file)
                suffix = Path(filename).suffix.lower()

                if suffix:
                    files_by_extension[suffix].append(rel_str)

                if filename in _CONFIG_FILES:
                    config_files.append(rel_str)

                    # Parse manifest contents for key config files
                    if filename == "package.json":
                        try:
                            manifest_contents["package_json"] = json.loads(
                                file_path.read_text(encoding="utf-8")
                            )
                        except (OSError, json.JSONDecodeError):
                            pass
                    elif filename == "pyproject.toml":
                        try:
                            manifest_contents["pyproject_toml"] = (
                                file_path.read_text(encoding="utf-8")
                            )
                        except OSError:
                            pass
                    elif filename == "requirements.txt":
                        try:
                            lines = file_path.read_text(encoding="utf-8").splitlines()
                            manifest_contents["requirements"] = [
                                line.strip()
                                for line in lines
                                if line.strip() and not line.startswith("#")
                            ]
                        except OSError:
                            pass

                if filename in _ENTRY_POINTS:
                    entry_points.append(rel_str)

        return {
            "folders": folders,
            "files_by_extension": dict(files_by_extension),
            "config_files": config_files,
            "entry_points": entry_points,
            "manifest_contents": manifest_contents,
            "top_level_folders": top_level_folders,
        }

    def identify_domains(
        self,
        structure: dict,
        graphify_data: dict,
    ) -> list[ObservedDomain]:
        """
        Derive domain boundaries from structural data and graphify output.
        Combines signals from multiple sources; assigns ConfidenceLevel based
        on how many independent signals agree on each domain boundary.
        """
        # candidates: {domain_name: {evidence, signals, files, from_folder}}
        candidates: dict[str, dict] = {}

        def add_signal(name: str, evidence: str, strength: int = 1) -> None:
            if name not in candidates:
                candidates[name] = {
                    "evidence": [],
                    "signals": 0,
                    "files": [],
                    "from_folder": False,
                }
            candidates[name]["evidence"].append(evidence)
            candidates[name]["signals"] += strength

        def add_files(name: str, prefix: str) -> None:
            """Collect all files under the given path prefix into a candidate."""
            for ext_files in structure.get("files_by_extension", {}).values():
                for f in ext_files:
                    if f.startswith(prefix):
                        candidates[name]["files"].append(f)

        # --- Signal 1: top-level folders ---
        top_level = structure.get("top_level_folders", [])
        for folder in top_level:
            norm = _normalize_name(folder)
            if norm in _NON_DOMAIN_FOLDERS:
                continue

            if norm in _CONTAINER_FOLDERS:
                # Container folders (src/, app/) hold domain subdirs — look inside
                container_path = self.project_path / folder
                try:
                    children = [c for c in container_path.iterdir() if c.is_dir()]
                except OSError:
                    children = []

                for child in children:
                    child_norm = _normalize_name(child.name)
                    if child_norm in _NON_DOMAIN_FOLDERS or child_norm.startswith("__"):
                        continue
                    child_rel = f"{folder}/{child.name}"
                    add_signal(child_norm, f"top-level folder: {child_rel}/")
                    candidates[child_norm]["from_folder"] = True
                    add_files(child_norm, child_rel + "/")
            else:
                # Non-container top-level folder is itself a domain candidate
                add_signal(norm, f"top-level folder: {folder}/")
                candidates[norm]["from_folder"] = True
                add_files(norm, folder + "/")

        # --- Signal 2: graphify communities ---
        for community_line in graphify_data.get("communities", []):
            # Lines are typically "cluster_name: file1, file2" or "cluster_name"
            name_part = community_line.split(":")[0].strip()
            norm = _normalize_name(name_part)
            if norm in _NON_DOMAIN_FOLDERS:
                continue
            # Extra strength if it aligns with an already-found folder
            if norm in candidates and candidates[norm].get("from_folder"):
                add_signal(norm, f"graphify community: {community_line}", strength=2)
            else:
                add_signal(norm, f"graphify community: {community_line}", strength=1)

        # --- Signal 3: config file signals ---
        requirements = structure.get("manifest_contents", {}).get("requirements", [])
        for req in requirements:
            pkg_name = (
                req.split("==")[0].split(">=")[0].split("<=")[0].strip().lower()
            )
            if pkg_name in _PACKAGE_DOMAIN_HINTS:
                domain_name = _PACKAGE_DOMAIN_HINTS[pkg_name]
                add_signal(domain_name, f"requirements: {pkg_name} found")

        package_json = structure.get("manifest_contents", {}).get("package_json", {})
        for script_name in package_json.get("scripts", {}):
            if ":" in script_name:
                # e.g. "build:api" hints at an "api" domain
                domain_hint = _normalize_name(script_name.split(":")[1])
                if domain_hint and domain_hint not in _NON_DOMAIN_FOLDERS:
                    add_signal(domain_hint, f"package.json script: {script_name}")

        # --- Signal 4: multiple entry points suggest multiple service domains ---
        entry_points = structure.get("entry_points", [])
        if len(entry_points) > 1:
            for ep in entry_points:
                parent = Path(ep).parent.name
                norm = _normalize_name(parent)
                if norm and norm not in _NON_DOMAIN_FOLDERS and norm != ".":
                    add_signal(norm, f"entry point: {ep}")

        # --- Signal 5: git signals ---
        for folder, count in self._git_signals.get("commit_frequency", {}).items():
            norm = _normalize_name(folder)
            if norm in candidates and count > 0:
                add_signal(norm, f"git: {count} commits in last 6 months")

        # --- Build ObservedDomain objects ---
        all_domain_names = set(candidates.keys())
        domains: list[ObservedDomain] = []

        for name, data in candidates.items():
            signals = data["signals"]
            if signals >= 3:
                confidence = ConfidenceLevel.HIGH
            elif signals >= 2:
                confidence = ConfidenceLevel.MEDIUM
            else:
                confidence = ConfidenceLevel.LOW

            purpose = _derive_purpose(name, data["evidence"], structure)
            deps = _find_cross_domain_deps(
                self.project_path,
                data["files"],
                all_domain_names - {name},
            )

            domains.append(ObservedDomain(
                name=name,
                purpose=purpose,
                confidence=confidence,
                evidence=data["evidence"],
                file_paths=data["files"],
                dependencies=deps,
            ))

        # Sort HIGH → MEDIUM → LOW
        domains.sort(key=lambda d: d.confidence.value)
        return domains

    def detect_patterns(
        self,
        structure: dict,
    ) -> list[DetectedPattern]:
        """
        Find repeated structures: repeated filenames, similar folder layouts,
        and oversized files (>500 lines).
        """
        patterns: list[DetectedPattern] = []

        all_files: list[str] = []
        for ext_files in structure.get("files_by_extension", {}).values():
            all_files.extend(ext_files)

        # --- Check 1: repeated filenames (excluding conventional ones) ---
        filename_locations: dict[str, list[str]] = defaultdict(list)
        for f in all_files:
            name = Path(f).name
            if name not in _CONVENTIONAL_FILENAMES:
                filename_locations[name].append(f)

        for name, locations in filename_locations.items():
            if len(locations) >= 3:
                patterns.append(DetectedPattern(
                    name=name,
                    pattern_type="component",
                    locations=locations,
                    instance_count=len(locations),
                    is_repetition=True,
                ))

        # --- Check 2: similar folder structures (Jaccard similarity > 70%) ---
        folder_contents: dict[str, set[str]] = defaultdict(set)
        for f in all_files:
            p = Path(f)
            parent = str(p.parent)
            folder_contents[parent].add(p.name)

        folder_list = [
            (folder, names)
            for folder, names in folder_contents.items()
            if len(names) >= 2 and folder != "."
        ]

        seen_pairs: set[frozenset] = set()
        for i, (folder_a, names_a) in enumerate(folder_list):
            for folder_b, names_b in folder_list[i + 1:]:
                pair_key = frozenset([folder_a, folder_b])
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                intersection = names_a & names_b
                union = names_a | names_b
                if not union:
                    continue
                similarity = len(intersection) / len(union)

                if similarity > 0.70:
                    pattern_name = (
                        f"folder_structure:"
                        f"{Path(folder_a).name}~{Path(folder_b).name}"
                    )
                    patterns.append(DetectedPattern(
                        name=pattern_name,
                        pattern_type="utility",
                        locations=[folder_a, folder_b],
                        instance_count=2,
                        is_repetition=True,
                    ))

        # --- Check 3: oversized files (>500 lines) ---
        oversized_extensions = {".py", ".ts", ".tsx", ".js", ".jsx"}
        candidate_files: list[str] = []
        for ext, ext_files in structure.get("files_by_extension", {}).items():
            if ext in oversized_extensions:
                candidate_files.extend(ext_files)

        for f in candidate_files:
            full_path = self.project_path / f
            try:
                with full_path.open(encoding="utf-8", errors="ignore") as fh:
                    line_count = sum(1 for _ in fh)
                if line_count > 500:
                    patterns.append(DetectedPattern(
                        name=Path(f).name,
                        pattern_type="oversized_file",
                        locations=[f],
                        instance_count=1,
                        is_repetition=False,
                    ))
            except OSError:
                continue

        return patterns

    def analyze_git_history(
        self,
    ) -> dict:
        """
        Read git log to extract commit frequency, co-change pairs, and
        recent activity signals. All subprocess calls have a 30s timeout.
        Returns empty dict signals gracefully on failure.
        """

        def run_git(*args: str) -> Optional[str]:
            try:
                result = subprocess.run(
                    ["git"] + list(args),
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    print(f"Warning: git command failed: git {' '.join(args)}")
                    return None
                return result.stdout
            except (subprocess.TimeoutExpired, OSError, FileNotFoundError) as exc:
                print(f"Warning: git command error: {exc}")
                return None

        commit_frequency: dict[str, int] = defaultdict(int)
        pair_counts: dict[tuple, int] = defaultdict(int)

        log_output = run_git(
            "log", "--format=%H", "--name-only", "--since=6 months ago"
        )

        if log_output:
            # Parse commit blocks: hash line, blank line, file lines, blank line
            state = "HASH"
            current_hash: Optional[str] = None
            current_files: list[str] = []

            def _process_commit(files: list[str]) -> None:
                top_dirs: set[str] = set()
                for f in files:
                    parts = Path(f).parts
                    if parts:
                        top_dirs.add(parts[0])
                for d in top_dirs:
                    commit_frequency[d] += 1
                for i, fa in enumerate(files):
                    for fb in files[i + 1:]:
                        pair = (min(fa, fb), max(fa, fb))
                        pair_counts[pair] += 1

            for line in log_output.splitlines():
                stripped = line.strip()
                is_hash = (
                    len(stripped) == 40
                    and all(c in "0123456789abcdef" for c in stripped)
                )

                if state == "HASH":
                    if is_hash:
                        current_hash = stripped
                        current_files = []
                        state = "AFTER_HASH"
                elif state == "AFTER_HASH":
                    if not stripped:
                        state = "FILES"
                    elif is_hash:
                        # No blank line — another hash immediately
                        if current_files:
                            _process_commit(current_files)
                        current_hash = stripped
                        current_files = []
                    else:
                        # File line without preceding blank (some git versions)
                        current_files.append(stripped)
                        state = "FILES"
                elif state == "FILES":
                    if not stripped:
                        if current_files:
                            _process_commit(current_files)
                        current_hash = None
                        current_files = []
                        state = "HASH"
                    elif is_hash:
                        if current_files:
                            _process_commit(current_files)
                        current_hash = stripped
                        current_files = []
                        state = "AFTER_HASH"
                    else:
                        current_files.append(stripped)

            # Handle last commit if no trailing blank line
            if current_files:
                _process_commit(current_files)

        # Top 20 co-change pairs with count > 2
        top_pairs = sorted(
            [(a, b, c) for (a, b), c in pair_counts.items() if c > 2],
            key=lambda x: x[2],
            reverse=True,
        )[:20]

        # Recent activity: which top-level folders had commits in last 3 months
        recent_activity: dict[str, bool] = {}
        recent_output = run_git(
            "log", "--format=%H %ai", "--name-only", "--since=3 months ago"
        )
        if recent_output:
            for line in recent_output.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                # File paths have a parent component; skip hash+date lines
                p = Path(stripped)
                if len(p.parts) >= 2:
                    recent_activity[p.parts[0]] = True

        return {
            "commit_frequency": dict(commit_frequency),
            "co_change_pairs": top_pairs,
            "recent_activity": recent_activity,
        }

    def identify_gaps(
        self,
        domains: list[ObservedDomain],
        structure: dict,
    ) -> list[DeveloperGap]:
        """
        Identify what cannot be determined from the codebase alone.
        Always produces the project purpose gap (BLOCKING).
        Conditionally produces gaps for inactive modules and duplication.
        Always produces the constraints gap (OPTIONAL).
        Filters by involvement_preference before returning.
        """
        gaps: list[DeveloperGap] = []

        # --- Gap 1: Project purpose (always BLOCKING) ---
        gaps.append(DeveloperGap(
            question=(
                "What is the primary purpose of this project and where is it headed? "
                "This becomes the root intent for all agents."
            ),
            severity=GapSeverity.BLOCKING,
            context="Cannot be inferred from code structure alone.",
            default_if_skipped=(
                "Purpose unclear — agents will operate with limited strategic context."
            ),
            affects=["project/vision.md", "project/state.md"],
        ))

        # --- Gap 2: Active vs deprecated modules (IMPORTANT, conditional) ---
        low_confidence_names = [
            d.name for d in domains if d.confidence == ConfidenceLevel.LOW
        ]
        recent_activity = self._git_signals.get("recent_activity", {})
        all_top_folders = structure.get("top_level_folders", [])

        # Only flag inactive folders if we actually have git data to compare against
        inactive_folders = []
        if recent_activity:
            inactive_folders = [
                f for f in all_top_folders
                if f not in _NON_DOMAIN_FOLDERS
                and not recent_activity.get(f, False)
            ]

        inactive_list = list({*low_confidence_names, *inactive_folders})
        if inactive_list:
            gaps.append(DeveloperGap(
                question=(
                    f"The following folders show low recent activity: "
                    f"{', '.join(inactive_list)}. "
                    "Are these deprecated, stable, or planned for future work?"
                ),
                severity=GapSeverity.IMPORTANT,
                context="Low activity could mean stable and complete, or abandoned.",
                default_if_skipped=(
                    "Treated as stable — will be included in roster with low priority."
                ),
                affects=["agents/index.md"],
            ))

        # --- Gap 3: Intentional duplication (IMPORTANT, conditional) ---
        # Approximate by looking for non-conventional filenames appearing 3+ times.
        # (detect_patterns is not passed here, so we derive this from structure.)
        all_files: list[str] = []
        for ext_files in structure.get("files_by_extension", {}).values():
            all_files.extend(ext_files)
        filename_counts = Counter(Path(f).name for f in all_files)
        repeated = [
            name for name, count in filename_counts.items()
            if count >= 3 and name not in _CONVENTIONAL_FILENAMES
        ]
        if repeated:
            gap_list = ", ".join(repeated[:5])
            gaps.append(DeveloperGap(
                question=(
                    f"The following patterns appear multiple times: {gap_list}. "
                    "Is this intentional or should these be consolidated?"
                ),
                severity=GapSeverity.IMPORTANT,
                context=(
                    "Bonsai will flag these for pruning unless confirmed intentional."
                ),
                default_if_skipped=(
                    "Treated as unintentional — flagged for pruning proposals."
                ),
                affects=["quality/repetition.md"],
            ))

        # --- Gap 4: Constraints (always OPTIONAL) ---
        gaps.append(DeveloperGap(
            question=(
                "Are there compliance, security, or data boundary constraints Bonsai "
                "should never violate? e.g. PII must not leave certain services, "
                "specific frameworks must be used."
            ),
            severity=GapSeverity.OPTIONAL,
            context="These become hard constraints in agent definitions.",
            default_if_skipped=(
                "No hard constraints assumed beyond standard best practices."
            ),
            affects=["agents/*.md"],
        ))

        # --- Filter by involvement_preference ---
        pref = self._involvement_preference.lower()
        if pref == "low":
            gaps = [g for g in gaps if g.severity == GapSeverity.BLOCKING]
        elif pref == "medium":
            gaps = [
                g for g in gaps
                if g.severity in (GapSeverity.BLOCKING, GapSeverity.IMPORTANT)
            ]
        # "high": return all gaps unchanged

        # Order: BLOCKING → IMPORTANT → OPTIONAL
        _order = {GapSeverity.BLOCKING: 0, GapSeverity.IMPORTANT: 1, GapSeverity.OPTIONAL: 2}
        gaps.sort(key=lambda g: _order[g.severity])
        return gaps

    def propose_roster(
        self,
        domains: list[ObservedDomain],
    ) -> list[str]:
        """
        Derive agent names from observed domains.
        One agent per HIGH or MEDIUM domain.
        LOW domains merge into nearest HIGH parent or become *_unverified_agent.
        Always includes quality and evaluator.
        """
        roster: list[str] = []

        high_medium = [
            d for d in domains
            if d.confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM)
        ]
        low_domains = [
            d for d in domains
            if d.confidence == ConfidenceLevel.LOW
        ]

        for domain in high_medium:
            roster.append(f"{domain.name}_agent")

        for domain in low_domains:
            # Merge into a HIGH/MEDIUM domain if that domain imports from this one
            merged = False
            for hm in high_medium:
                if domain.name in hm.dependencies:
                    merged = True
                    break
            if not merged:
                roster.append(f"{domain.name}_unverified_agent")

        # Always include these two regardless of domains
        if "quality" not in roster:
            roster.append("quality")
        if "evaluator" not in roster:
            roster.append("evaluator")

        return roster

    def write_to_roots(
        self,
        output: ReconnaissanceOutput,
    ) -> None:
        """
        Write reconnaissance findings to roots/ via RootManager, in order:
        codebase entries → dependency entries → patterns → project state → agent files.
        Writes agent .md files directly with pathlib (no writer method for these yet).
        """
        today = today_iso()

        # --- Codebase entries ---
        for domain in output.observed_domains:
            self.root_manager.writer.update_codebase_entry(
                CodebaseEntry(
                    module=domain.name,
                    purpose=domain.purpose,
                    owner_agent=f"{domain.name}_agent",
                    status="discovered",
                    last_modified=today,
                )
            )

        # --- Dependency entries ---
        for domain in output.observed_domains:
            self.root_manager.writer.update_dependency_entry(
                DependencyEntry(
                    component=domain.name,
                    depends_on=domain.dependencies,
                    depended_on_by=[],
                    criticality="medium",
                )
            )

        # --- Pattern entries ---
        for pattern in output.detected_patterns:
            self.root_manager.writer.append_pattern(
                component_name=pattern.name,
                purpose=pattern.pattern_type,
                interface_shape="detected",
                location=pattern.locations[0] if pattern.locations else "",
            )

        # --- Project state ---
        self.root_manager.writer.update_project_state(
            ProjectState(
                phase="Phase 3 — Reconnaissance complete",
                completed=[
                    "Reconnaissance scan",
                    f"{len(output.observed_domains)} domains identified",
                ],
                in_progress=[],
                next_priority=(
                    "Developer gap resolution"
                    if not output.ready_to_proceed
                    else "Agent roster approval and build start"
                ),
                blockers=[
                    g.question
                    for g in output.developer_gaps
                    if g.severity == GapSeverity.BLOCKING
                ],
                last_session_summary=output.confidence_summary,
            )
        )

        # --- Agent .md files ---
        roots_path = self.root_manager.roots_path
        agents_dir = roots_path / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        domain_purpose: dict[str, str] = {
            d.name: d.purpose for d in output.observed_domains
        }

        for agent_name in output.proposed_roster:
            agent_file = agents_dir / f"{agent_name}.md"

            if agent_name == "quality":
                purpose_str = "Quality and pattern analysis"
                domain_name = "quality"
            elif agent_name == "evaluator":
                purpose_str = "Synthetic evaluation and testing"
                domain_name = "evaluator"
            else:
                # Strip _agent or _unverified_agent suffix to recover domain name
                domain_name = (
                    agent_name
                    .replace("_unverified_agent", "")
                    .replace("_agent", "")
                )
                purpose_str = domain_purpose.get(
                    domain_name, "Purpose unclear — requires developer input"
                )

            content = (
                f"# {agent_name}\n\n"
                f"## Domain\n"
                f"{purpose_str}\n\n"
                f"## Skills\n"
                f"- To be defined after developer gap resolution\n\n"
                f"## Rules\n"
                f"- Never modifies another agent's domain\n"
                f"- Always updates roots/ after acting\n"
                f"- Reads relevant roots/ files before acting\n\n"
                f"## Reads From\n"
                f"- roots/context/codebase.md\n"
                f"- roots/context/patterns.md\n\n"
                f"## Writes To\n"
                f"- src/{domain_name}/\n\n"
                f"## Never Touches\n"
                f"- To be defined after roster approval\n"
            )

            try:
                agent_file.write_text(content, encoding="utf-8")
            except OSError as exc:
                print(f"Warning: could not write agent file {agent_file}: {exc}")

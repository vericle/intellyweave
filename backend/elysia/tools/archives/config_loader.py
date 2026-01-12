"""
Configuration loader for archive domains.

Loads the archive_domains.yaml configuration file and provides
utilities for accessing domain lists and default configurations.
"""

import os
from pathlib import Path
from typing import Optional

import yaml

from elysia.tools.archives.types import (
    AccessLevel,
    DigitizationStatus,
    Protocol,
    ArchiveSource,
    ArchiveConstraint,
)


class ArchiveConfigLoader:
    """Loads and manages archive domain configuration."""

    _instance: Optional["ArchiveConfigLoader"] = None
    _config: Optional[dict] = None

    def __new__(cls) -> "ArchiveConfigLoader":
        """Singleton pattern to avoid reloading config."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        # Try multiple paths for the config file
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "config" / "archive_domains.yaml",
            Path(__file__).parent.parent.parent / "config" / "archive_domains.yaml",
            Path(os.getcwd()) / "config" / "archive_domains.yaml",
            Path(os.getcwd()) / "backend" / "config" / "archive_domains.yaml",
        ]

        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break

        if config_path is None:
            raise FileNotFoundError(
                f"archive_domains.yaml not found. Tried: {[str(p) for p in possible_paths]}"
            )

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    @property
    def config(self) -> dict:
        """Get the full configuration."""
        if self._config is None:
            self._load_config()
        return self._config  # type: ignore

    def get_groups(self) -> list[str]:
        """Get list of all archive group names."""
        return list(self.config.get("groups", {}).keys())

    def get_group_domains(self, group_name: str) -> list[str]:
        """Get list of domains for a specific group."""
        group = self.config.get("groups", {}).get(group_name, {})
        domains = group.get("domains", [])
        return [d.get("domain", d) if isinstance(d, dict) else d for d in domains]

    def get_all_domains(self) -> list[str]:
        """Get flat list of all archive domains."""
        all_domains = []
        for group_name in self.get_groups():
            all_domains.extend(self.get_group_domains(group_name))
        return all_domains

    def get_domains_for_groups(self, group_names: list[str]) -> list[str]:
        """Get domains for specific groups."""
        domains = []
        for group_name in group_names:
            domains.extend(self.get_group_domains(group_name))
        return domains

    def get_domain_config(self, domain: str) -> Optional[dict]:
        """Get full configuration for a specific domain."""
        for group_name in self.get_groups():
            group = self.config.get("groups", {}).get(group_name, {})
            for d in group.get("domains", []):
                if isinstance(d, dict) and d.get("domain") == domain:
                    return {**d, "group": group_name}
                elif d == domain:
                    return {"domain": domain, "group": group_name}
        return None

    def get_access_instructions(self, domain: str) -> Optional[dict]:
        """Get access instructions for a specific domain from config.

        Returns the access_instructions block from archive_domains.yaml if present,
        or None if not configured. For DISCOVERED sources (not in config), returns None
        so the caller can use DSPy to generate instructions.

        Args:
            domain: The domain name to look up

        Returns:
            Dict with 'type' and 'steps' if configured, None otherwise
        """
        config = self.get_domain_config(domain)
        if config is None:
            return None

        access_instructions = config.get("access_instructions")
        if access_instructions is None:
            return None

        # Normalize the structure
        return {
            "type": access_instructions.get("type", "online_search"),
            "steps": access_instructions.get("steps", []),
        }

    def get_group_descriptions(self) -> dict[str, str]:
        """Get a mapping of group names to their descriptions.

        This is used by QueryIntentAnalyzer to understand what each archive
        group contains and select relevant groups for a query.

        Returns:
            Dict mapping group name to description string
        """
        descriptions = {}
        for group_name in self.get_groups():
            group = self.config.get("groups", {}).get(group_name, {})
            descriptions[group_name] = group.get("description", f"Archives in {group_name}")
        return descriptions

    def get_archives_for_groups(self, group_names: list[str]) -> list[dict]:
        """Get full archive metadata for specific groups.

        Returns complete metadata for each archive (name, domain, access_level,
        digitization_status, protocol, notes) for use by ArchivePrioritizer.

        Args:
            group_names: List of group names to fetch archives for

        Returns:
            List of archive dicts with full metadata
        """
        archives = []
        for group_name in group_names:
            if group_name not in self.get_groups():
                continue

            group = self.config.get("groups", {}).get(group_name, {})
            for d in group.get("domains", []):
                if isinstance(d, dict):
                    archive = {
                        "domain": d.get("domain", ""),
                        "name": d.get("name", d.get("domain", "")),
                        "access_level": d.get("default_access_level", "PUBLIC_OPEN"),
                        "digitization_status": d.get("default_digitization_status", "N_A"),
                        "protocol": d.get("default_protocol", "HTML_CONTENT"),
                        "notes": d.get("notes", ""),
                        "group": group_name,
                    }
                    archives.append(archive)
                else:
                    # Simple domain string
                    archives.append({
                        "domain": d,
                        "name": d,
                        "access_level": "PUBLIC_OPEN",
                        "digitization_status": "N_A",
                        "protocol": "HTML_CONTENT",
                        "notes": "",
                        "group": group_name,
                    })
        return archives

    def get_all_archives_metadata(self) -> list[dict]:
        """Get full metadata for all configured archives.

        Returns:
            List of archive dicts with full metadata from all groups
        """
        return self.get_archives_for_groups(self.get_groups())

    def create_archive_source_skeleton(
        self,
        domain: str,
        search_result: Optional[dict] = None,
    ) -> ArchiveSource:
        """
        Create an ArchiveSource with defaults from config.

        Args:
            domain: The domain name
            search_result: Optional search result to populate summary/notes

        Returns:
            ArchiveSource with defaults populated from config
        """
        config = self.get_domain_config(domain) or {}

        # Parse access level (default to PUBLIC_OPEN for discovered sources)
        access_level_str = config.get("default_access_level", "PUBLIC_OPEN")
        try:
            access_level = AccessLevel(access_level_str)
        except ValueError:
            access_level = AccessLevel.PUBLIC_OPEN

        # Parse digitization status
        dig_status_str = config.get("default_digitization_status", "N_A")
        try:
            digitization_status = DigitizationStatus(dig_status_str)
        except ValueError:
            digitization_status = DigitizationStatus.N_A

        # Parse protocol
        protocol_str = config.get("default_protocol", "HTML_CONTENT")
        try:
            protocol = Protocol(protocol_str)
        except ValueError:
            protocol = Protocol.HTML_CONTENT

        # Build source
        return ArchiveSource(
            id=f"src_{domain.replace('.', '_')}",
            name=config.get("name", domain),
            domain=domain,
            group=config.get("group", "DISCOVERED"),
            summary=search_result.get("content", "") if search_result else "",
            access_level=access_level,
            digitization_status=digitization_status,
            protocol=protocol,
            constraints=[],
            notes=config.get("notes", ""),
            source_urls=[search_result.get("url", "")] if search_result else [],
        )


def get_archive_domains(groups: Optional[list[str]] = None) -> list[str]:
    """
    Convenience function to get archive domains.

    Args:
        groups: Optional list of group names to filter by.
                If None, returns all domains.

    Returns:
        List of domain strings
    """
    loader = ArchiveConfigLoader()
    if groups:
        return loader.get_domains_for_groups(groups)
    return loader.get_all_domains()


def get_archive_config() -> dict:
    """Get the full archive configuration."""
    return ArchiveConfigLoader().config


def get_archive_config_yaml() -> str:
    """Get the raw YAML content of the archive configuration."""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "archive_domains.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return f.read()

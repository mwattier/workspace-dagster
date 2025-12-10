#!/usr/bin/env python3
"""
Dagster Module Builder - Core Implementation

This script automates the creation of Dagster modules with:
- Base module structure
- Custom IO manager
- PostgreSQL/MySQL database
- Workspace integration
- Deployment configurations
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ModuleBuilder:
    """Main class for building Dagster modules."""

    def __init__(self, templates_dir: str = None):
        """Initialize the module builder."""
        if templates_dir is None:
            # Default to ~/workspace/patterns/dagster
            templates_dir = os.path.expanduser("~/workspace/patterns/dagster")

        self.templates_dir = Path(templates_dir)
        self.workspace_dir = Path.home() / "workspace"
        self.projects_dir = self.workspace_dir / "projects"
        self.services_dir = self.workspace_dir / "services" / "dagster"

    def substitute_placeholders(self, content: str, variables: Dict[str, str]) -> str:
        """Replace all placeholders in content with actual values."""
        for key, value in variables.items():
            content = content.replace(key, value)
        return content

    def to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Replace hyphens with underscores
        name = name.replace('-', '_')
        # Insert underscore before uppercase letters and convert to lowercase
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()

    def to_upper_snake_case(self, name: str) -> str:
        """Convert name to UPPER_SNAKE_CASE."""
        return self.to_snake_case(name).upper()

    def to_title_case(self, name: str) -> str:
        """Convert name to Title Case."""
        # Replace hyphens and underscores with spaces
        name = name.replace('-', ' ').replace('_', ' ')
        # Capitalize each word
        return ' '.join(word.capitalize() for word in name.split())

    def get_next_available_port(self, base_port: int = 5440) -> int:
        """
        Scan workspace .env for used PostgreSQL ports and return next available.

        Args:
            base_port: Starting port number (default 5440)

        Returns:
            Next available port number
        """
        env_file = self.services_dir / ".env"

        if not env_file.exists():
            return base_port

        used_ports = []

        with open(env_file, 'r') as f:
            for line in f:
                # Match PORT= lines
                match = re.search(r'PORT=(\d+)', line)
                if match:
                    port = int(match.group(1))
                    # Only consider PostgreSQL ports (5400-5500 range)
                    if 5400 <= port <= 5500:
                        used_ports.append(port)

        if not used_ports:
            return base_port

        max_port = max(used_ports)
        return max(max_port + 1, base_port)

    def generate_variables(
        self,
        module_name: str,
        database_type: str,
        description: str = "",
        deploy_name: str = "",
        client_name: str = "",
        git_repo: str = "",
    ) -> Dict[str, str]:
        """
        Generate all template variables.

        Args:
            module_name: Name of the module (can be kebab-case or snake_case)
            database_type: Type of database (postgresql/mysql/none)
            description: Module description
            deploy_name: Deployment name (e.g., "production")
            client_name: Client name
            git_repo: Git repository URL

        Returns:
            Dictionary of template variables
        """
        # Normalize module name to snake_case for internal use
        module_snake = self.to_snake_case(module_name)

        # Determine database port
        db_port = "5440"  # Default, should call get_next_available_port()
        if database_type == "mysql":
            db_port = "3307"  # MySQL default
        elif database_type == "postgresql":
            db_port = str(self.get_next_available_port())

        variables = {
            # Module names
            "__MODULE_NAME__": module_snake,
            "__MODULE_NAME_UPPER__": self.to_upper_snake_case(module_name),
            "__MODULE_TITLE__": self.to_title_case(module_name),
            "__MODULE_DESCRIPTION__": description or f"{self.to_title_case(module_name)} Dagster module",

            # Database variables
            "__DB_TYPE__": database_type,
            "__DB_PORT__": db_port,
            "__DB_NAME__": f"{module_snake}_db",
            "__DB_USER__": f"{module_snake}_user",
            "__DB_PASSWORD__": f"{module_snake}_password",

            # Deployment variables
            "__DEPLOY_NAME__": deploy_name or "production",
            "__CLIENT_NAME__": client_name or "Client Name",
            "__GIT_REPOSITORY__": git_repo or f"git@github.com:myorg/{module_name}.git",
            "__REMOTE_HOST__": "<REMOTE_HOST>",
            "__REMOTE_USER__": "<REMOTE_USER>",
            "__REMOTE_BASE_PATH__": "/opt/dagster",
            "__NETWORK_NAME__": "workspace-net",
        }

        return variables

    def process_template_file(
        self,
        template_path: Path,
        output_path: Path,
        variables: Dict[str, str]
    ) -> None:
        """
        Process a single template file.

        Args:
            template_path: Path to template file
            output_path: Path to output file
            variables: Template variables
        """
        # Read template
        with open(template_path, 'r') as f:
            content = f.read()

        # Substitute placeholders
        processed = self.substitute_placeholders(content, variables)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write output
        with open(output_path, 'w') as f:
            f.write(processed)

    def copy_directory_recursive(
        self,
        source_dir: Path,
        target_dir: Path,
        variables: Dict[str, str]
    ) -> List[Path]:
        """
        Recursively copy and process template directory.

        Args:
            source_dir: Source template directory
            target_dir: Target output directory
            variables: Template variables

        Returns:
            List of created files
        """
        created_files = []

        # Walk through source directory
        for item in source_dir.rglob('*'):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(source_dir)

                # Substitute placeholders in path
                output_rel_path = str(rel_path)
                for key, value in variables.items():
                    output_rel_path = output_rel_path.replace(key, value)

                # Remove .template extension if present
                if output_rel_path.endswith('.template'):
                    output_rel_path = output_rel_path[:-9]

                output_path = target_dir / output_rel_path

                # Process template file
                self.process_template_file(item, output_path, variables)
                created_files.append(output_path)

        return created_files


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: module_builder.py <module-name>")
        sys.exit(1)

    module_name = sys.argv[1]

    builder = ModuleBuilder()

    print(f"Creating module: {module_name}")
    print(f"Templates: {builder.templates_dir}")
    print(f"Output: {builder.projects_dir / module_name}")

    # Generate variables
    variables = builder.generate_variables(
        module_name=module_name,
        database_type="postgresql",
        description="Test module created with automation",
    )

    print("\nVariables:")
    for key, value in variables.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

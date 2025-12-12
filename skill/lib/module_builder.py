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

    def create_module(
        self,
        module_name: str,
        database_type: str = "postgresql",
        description: str = "",
        integrate_workspace: bool = False,
        configure_deployment: bool = False,
        deploy_name: str = "production",
        client_name: str = "",
        git_repo: str = "",
    ) -> bool:
        """
        Create a complete Dagster module from templates.

        Args:
            module_name: Name of the module (kebab-case or snake_case)
            database_type: Database type (postgresql/mysql/none)
            description: Module description
            integrate_workspace: Whether to create workspace integration files
            configure_deployment: Whether to create deployment configs
            deploy_name: Deployment name (e.g., "production", "yoda")
            client_name: Client name
            git_repo: Git repository URL

        Returns:
            True if successful, False otherwise
        """
        module_snake = self.to_snake_case(module_name)
        module_dir = self.projects_dir / module_name

        # Check if module already exists
        if module_dir.exists():
            print(f"Error: Module {module_name} already exists at {module_dir}")
            return False

        # Generate all variables
        variables = self.generate_variables(
            module_name=module_name,
            database_type=database_type,
            description=description,
            deploy_name=deploy_name,
            client_name=client_name,
            git_repo=git_repo,
        )

        print(f"\nCreating module: {module_name}")
        print(f"  Snake case: {module_snake}")
        print(f"  Database: {database_type}")
        if database_type != "none":
            print(f"  Port: {variables['__DB_PORT__']}")
        print()

        # Create base module structure
        print("Creating base module...")
        base_dir = self.templates_dir / "base"
        if base_dir.exists():
            created_files = self.copy_directory_recursive(base_dir, module_dir, variables)
            print(f"  Created {len(created_files)} files")
        else:
            print(f"  Warning: Base templates not found at {base_dir}")

        # Create workspace integration if requested
        if integrate_workspace:
            print("\nCreating workspace integration...")
            workspace_dir = self.templates_dir / "workspace-integration"
            if workspace_dir.exists():
                workspace_target = module_dir / "workspace" / "local"
                created_files = self.copy_directory_recursive(workspace_dir, workspace_target, variables)
                print(f"  Created {len(created_files)} workspace files")
            else:
                print(f"  Warning: Workspace templates not found at {workspace_dir}")

        # Create deployment config if requested
        if configure_deployment:
            print(f"\nCreating deployment configuration for {deploy_name}...")
            deploy_template_dir = self.templates_dir / "deploy-strategies" / "git"  # Default to git strategy
            if deploy_template_dir.exists():
                deploy_target = module_dir / "deploy" / deploy_name
                created_files = self.copy_directory_recursive(deploy_template_dir, deploy_target, variables)
                print(f"  Created {len(created_files)} deployment files")
            else:
                print(f"  Warning: Deployment templates not found at {deploy_template_dir}")

        # Add database addon if needed
        if database_type in ["postgresql", "mysql"]:
            print(f"\nAdding {database_type} database configuration...")
            db_addon_dir = self.templates_dir / "addons" / f"database-{database_type}"
            if db_addon_dir.exists():
                created_files = self.copy_directory_recursive(db_addon_dir, module_dir, variables)
                print(f"  Created {len(created_files)} database files")

        print("\n" + "=" * 50)
        print("Module creation complete!")
        print("=" * 50)
        print(f"\nModule location: {module_dir}")
        print("\nNext steps:")
        print(f"1. Review generated files")
        if integrate_workspace:
            print(f"2. Append workspace/local/workspace.yaml to {self.services_dir}/workspace.yaml")
            print(f"3. Append workspace/local/.env to {self.services_dir}/.env")
            print(f"4. Rebuild and restart: cd {self.services_dir} && docker compose up -d --build")
        else:
            print(f"2. Integrate with workspace using: @dagster-module-builder workspace add {module_name}")
        print()

        return True


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Create a new Dagster module from templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create basic module with PostgreSQL
  %(prog)s my-new-module

  # Create module without database
  %(prog)s my-module --db none

  # Create module with workspace integration
  %(prog)s my-module --workspace

  # Full module with deployment config
  %(prog)s my-module --workspace --deploy --deploy-name yoda
        '''
    )

    parser.add_argument('module_name', help='Name of the module (e.g., my-module)')
    parser.add_argument('--db', '--database', dest='database_type',
                       choices=['postgresql', 'mysql', 'none'],
                       default='postgresql',
                       help='Database type (default: postgresql)')
    parser.add_argument('--desc', '--description', dest='description',
                       default='',
                       help='Module description')
    parser.add_argument('--workspace', action='store_true',
                       help='Create workspace integration files')
    parser.add_argument('--deploy', action='store_true',
                       help='Create deployment configuration')
    parser.add_argument('--deploy-name', default='production',
                       help='Deployment name (default: production)')
    parser.add_argument('--client', dest='client_name',
                       default='',
                       help='Client name for deployment')
    parser.add_argument('--git-repo', default='',
                       help='Git repository URL')
    parser.add_argument('--templates-dir',
                       help='Templates directory (default: ~/workspace/patterns/dagster)')

    args = parser.parse_args()

    # Initialize builder
    if args.templates_dir:
        builder = ModuleBuilder(templates_dir=args.templates_dir)
    else:
        builder = ModuleBuilder()

    # Create module
    success = builder.create_module(
        module_name=args.module_name,
        database_type=args.database_type,
        description=args.description,
        integrate_workspace=args.workspace,
        configure_deployment=args.deploy,
        deploy_name=args.deploy_name,
        client_name=args.client_name,
        git_repo=args.git_repo,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

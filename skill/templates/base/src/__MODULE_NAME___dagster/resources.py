"""
Custom IO Manager for Beast HubSpot module.

This IO manager stores asset outputs in a mounted directory (/tmp/dagster_storage/)
to ensure persistence across Docker container executions.

CRITICAL: This custom IO manager is MANDATORY for Docker-based deployments.
The default IO manager stores data in unmounted directories, causing downstream
assets to fail with "file not found" errors.
"""

import os
import pickle
from pathlib import Path
from typing import Any

from dagster import ConfigurableIOManager, InputContext, OutputContext, io_manager


class BeastHubspotIOManager(ConfigurableIOManager):
    """
    Custom IO Manager for Beast HubSpot assets.

    Stores asset outputs as pickle files in /tmp/dagster_storage/ which is
    mounted to the host for persistence across container executions.

    Features:
    - Handles both partitioned and non-partitioned assets
    - Properly resolves upstream asset keys when loading inputs
    - Comprehensive error messages with all attempted paths
    - Automatic directory creation
    """

    base_path: str = "/tmp/dagster_storage"

    def _get_path(self, context) -> str:
        """Generate file path for an asset."""
        # Get the asset key path (e.g., ["beast_hubspot", "my_asset"])
        asset_key_path = context.asset_key.path
        asset_name = asset_key_path[-1]  # Just the asset name

        # Create the base directory if it doesn't exist
        Path(self.base_path).mkdir(parents=True, exist_ok=True)

        # Check if this asset is partitioned
        partition_key = None
        try:
            if hasattr(context, 'partition_key') and context.partition_key:
                partition_key = context.partition_key
        except Exception:
            partition_key = None

        # Build file path
        if partition_key:
            return os.path.join(self.base_path, f"{asset_name}_{partition_key}.pickle")
        else:
            return os.path.join(self.base_path, f"{asset_name}.pickle")

    def handle_output(self, context: OutputContext, obj: Any) -> None:
        """Store the asset output."""
        file_path = self._get_path(context)

        # Store the data with metadata
        storage_obj = {
            'data': obj,
            'type': type(obj).__name__,
        }

        with open(file_path, 'wb') as f:
            pickle.dump(storage_obj, f)

        context.log.info(f"Stored {type(obj).__name__} to {file_path}")

    def load_input(self, context: InputContext) -> Any:
        """Load the asset input."""
        # CRITICAL: For input contexts, get the upstream asset's key
        # (not the current asset's key)
        if hasattr(context, 'upstream_output') and context.upstream_output:
            asset_name = context.upstream_output.asset_key.path[-1]
        else:
            # Fallback for non-asset inputs
            asset_name = context.asset_key.path[-1]

        # Try different path variations
        file_paths_to_try = []

        # Try non-partitioned path first
        file_paths_to_try.append(os.path.join(self.base_path, f"{asset_name}.pickle"))

        # Try partitioned path if partition key exists
        partition_key = None
        try:
            if hasattr(context, 'partition_key') and context.partition_key:
                partition_key = context.partition_key
        except Exception:
            partition_key = None

        if partition_key:
            file_paths_to_try.append(os.path.join(self.base_path, f"{asset_name}_{partition_key}.pickle"))

        # Try to load from each path
        storage_obj = None
        file_path = None
        for try_path in file_paths_to_try:
            if os.path.exists(try_path):
                file_path = try_path
                with open(file_path, 'rb') as f:
                    storage_obj = pickle.load(f)
                break

        if storage_obj is None:
            tried_paths = ", ".join(file_paths_to_try)
            raise FileNotFoundError(f"No stored data found. Tried paths: {tried_paths}")

        # Handle legacy pickled objects (direct data)
        if not isinstance(storage_obj, dict) or 'data' not in storage_obj:
            context.log.warning("Loading legacy pickled data format")
            return storage_obj

        data = storage_obj['data']
        context.log.info(f"Loaded {type(data).__name__} from {file_path}")
        return data


@io_manager
def beast_hubspot_io_manager() -> BeastHubspotIOManager:
    """IO Manager factory for Beast HubSpot assets."""
    storage_path = os.environ.get('DAGSTER_STORAGE_PATH', '/tmp/dagster_storage')
    return BeastHubspotIOManager(base_path=storage_path)

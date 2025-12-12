"""
Shared Metabase API Resource for Dagster Modules

This resource provides centralized access to Metabase API for querying
saved cards/questions. It can be reused across multiple Dagster modules.

Usage in your module:

```python
from dagster import asset, Definitions
from ...patterns.dagster.shared_resources.metabase_resource import metabase_resource

@asset(required_resource_keys={"metabase"})
def my_data_asset(context):
    metabase = context.resources.metabase
    card_id = int(os.environ["MY_MODULE_METABASE_CARD_ID"])
    data = metabase.query_card(card_id, format='json')
    return data

defs = Definitions(
    assets=[my_data_asset],
    resources={
        "metabase": metabase_resource,
    }
)
```

Environment Variables:
    METABASE_URL - Metabase instance URL
    METABASE_API_KEY - Metabase API key
"""

import os
import requests
from io import StringIO
from typing import Dict, Any, List, Union
from dagster import resource, ConfigurableResource, Failure
import pandas as pd


class MetabaseResource(ConfigurableResource):
    """
    Resource for querying Metabase API.

    Configuration:
        base_url: Metabase instance URL (from METABASE_URL)
        api_key: Metabase API key (from METABASE_API_KEY)
    """

    base_url: str
    api_key: str

    def query_card(self, card_id: int, format: str = 'json', timeout: int = 30) -> Union[List[Dict], pd.DataFrame, str]:
        """
        Execute a Metabase card/question and return results.

        Args:
            card_id: The Metabase card ID to query
            format: Output format - 'json' (list of dicts), 'csv' (string), or 'dataframe' (pandas DataFrame)
            timeout: Request timeout in seconds

        Returns:
            - If format='json': List of dictionaries (one per row)
            - If format='csv': CSV string
            - If format='dataframe': pandas DataFrame

        Raises:
            Failure: If the request fails or returns an error

        Example:
            ```python
            metabase = context.resources.metabase

            # Get as list of dicts
            data = metabase.query_card(593, format='json')

            # Get as DataFrame
            df = metabase.query_card(593, format='dataframe')

            # Get as CSV string
            csv_data = metabase.query_card(593, format='csv')
            ```
        """
        try:
            # Map dataframe format to csv for the API call
            api_format = 'csv' if format == 'dataframe' else format

            if api_format not in ['json', 'csv']:
                raise ValueError(f"Unsupported format: {format}. Use 'json', 'csv', or 'dataframe'")

            url = f"{self.base_url}/api/card/{card_id}/query/{api_format}"

            response = requests.post(
                url,
                headers={"X-API-KEY": self.api_key},
                timeout=timeout
            )

            # Check for errors
            if response.status_code != 200:
                raise Failure(
                    description=f"Metabase API request failed with status {response.status_code}",
                    metadata={
                        "card_id": card_id,
                        "format": format,
                        "status_code": response.status_code,
                        "response": response.text[:500],
                        "url": url,
                    }
                )

            # Process response based on format
            if format == 'json':
                return response.json()
            elif format == 'csv':
                return response.text
            elif format == 'dataframe':
                return pd.read_csv(StringIO(response.text))

        except requests.exceptions.Timeout:
            raise Failure(
                description=f"Metabase API request timed out after {timeout} seconds",
                metadata={
                    "card_id": card_id,
                    "timeout": timeout,
                    "hint": "Try increasing timeout or check Metabase server status"
                }
            )
        except requests.exceptions.ConnectionError as e:
            raise Failure(
                description="Failed to connect to Metabase server",
                metadata={
                    "base_url": self.base_url,
                    "error": str(e),
                    "hint": "Check METABASE_URL and network connectivity"
                }
            )
        except ValueError as e:
            raise Failure(
                description=str(e),
                metadata={"card_id": card_id, "format": format}
            )
        except Exception as e:
            raise Failure(
                description=f"Unexpected error querying Metabase: {str(e)}",
                metadata={
                    "card_id": card_id,
                    "format": format,
                    "error_type": type(e).__name__,
                }
            )

    def get_card_metadata(self, card_id: int) -> Dict[str, Any]:
        """
        Get metadata about a Metabase card (name, description, database, etc.)

        Args:
            card_id: The Metabase card ID

        Returns:
            Dictionary with card metadata

        Example:
            ```python
            metadata = metabase.get_card_metadata(593)
            print(f"Card name: {metadata['name']}")
            print(f"Database: {metadata['database_id']}")
            ```
        """
        try:
            url = f"{self.base_url}/api/card/{card_id}"

            response = requests.get(
                url,
                headers={"X-API-KEY": self.api_key},
                timeout=10
            )

            if response.status_code != 200:
                raise Failure(
                    description=f"Failed to get card metadata: {response.status_code}",
                    metadata={
                        "card_id": card_id,
                        "status_code": response.status_code,
                        "response": response.text[:500],
                    }
                )

            return response.json()

        except Exception as e:
            raise Failure(
                description=f"Error getting card metadata: {str(e)}",
                metadata={"card_id": card_id, "error_type": type(e).__name__}
            )


@resource
def metabase_resource() -> MetabaseResource:
    """
    Dagster resource for Metabase API access.

    Reads configuration from environment variables:
        - METABASE_URL: Metabase instance URL
        - METABASE_API_KEY: Metabase API key

    Returns:
        Configured MetabaseResource instance

    Raises:
        Failure: If required environment variables are missing
    """
    base_url = os.environ.get("METABASE_URL")
    api_key = os.environ.get("METABASE_API_KEY")

    if not base_url:
        raise Failure(
            description="Missing required environment variable: METABASE_URL",
            metadata={
                "hint": "Set METABASE_URL to your Metabase instance URL",
                "example": "METABASE_URL=https://metabase.example.com"
            }
        )

    if not api_key:
        raise Failure(
            description="Missing required environment variable: METABASE_API_KEY",
            metadata={
                "hint": "Set METABASE_API_KEY to your Metabase API key",
                "example": "METABASE_API_KEY=mb_xxx..."
            }
        )

    return MetabaseResource(
        base_url=base_url.rstrip('/'),  # Remove trailing slash
        api_key=api_key
    )

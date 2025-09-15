from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


# Import from the submodule without installing as a site package.
# We rely on the checked-in submodule under external/Repacss-power-profiling.
# The repo organizes code under src/, so we import via a relative path package-style
# by manipulating sys.path only within this module.
import os
import sys


def _ensure_submodule_on_path() -> None:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    submodule_src = os.path.join(project_root, "external", "Repacss-power-profiling", "src")
    if submodule_src not in sys.path:
        sys.path.insert(0, submodule_src)


_ensure_submodule_on_path()

try:
    from core.client import REPACSSPowerClient, DatabaseConfig, SSHConfig  # type: ignore
except Exception as import_error:  # pragma: no cover
    raise ImportError(
        "Failed to import REPACSS submodule. Ensure git submodules are initialized and the "
        "path external/Repacss-power-profiling/src exists."
    ) from import_error


@dataclass
class IDRACQueryParams:
    node_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100


class IDRACRemoteClient:
    """
    Minimal wrapper around REPACSSPowerClient for out-of-band queries used by this project.
    """

    def __init__(
        self,
        db_host: str,
        db_port: int,
        database: str,
        db_user: str,
        db_password: str,
        ssh_hostname: str,
        ssh_port: int,
        ssh_username: str,
        ssh_private_key_path: str,
        ssh_passphrase: str = "",
        ssl_mode: str = "prefer",
        schema: str = "idrac",
    ) -> None:
        self._db_config = DatabaseConfig(
            host=db_host,
            port=db_port,
            database=database,
            username=db_user,
            password=db_password,
            ssl_mode=ssl_mode,
            schema=schema,
        )
        self._ssh_config = SSHConfig(
            hostname=ssh_hostname,
            port=ssh_port,
            username=ssh_username,
            private_key_path=ssh_private_key_path,
            passphrase=ssh_passphrase,
            keepalive_interval=60,
        )
        self._client = REPACSSPowerClient(self._db_config, self._ssh_config, schema=schema)

    def __enter__(self) -> "IDRACRemoteClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.disconnect()

    def connect(self) -> None:
        self._client.connect()

    def disconnect(self) -> None:
        self._client.disconnect()

    # High-level helpers returning typed dicts for this project
    def fetch_computepower(self, params: IDRACQueryParams) -> List[Dict[str, Any]]:
        return self._client.get_computepower_metrics(
            node_id=params.node_id,
            start_time=params.start_time,
            end_time=params.end_time,
            limit=params.limit,
        )

    def fetch_boardtemperature(self, params: IDRACQueryParams) -> List[Dict[str, Any]]:
        return self._client.get_boardtemperature_metrics(
            node_id=params.node_id,
            start_time=params.start_time,
            end_time=params.end_time,
            limit=params.limit,
        )

    def summary_node(self, node_id: str) -> Dict[str, Any]:
        return self._client.get_computepower_summary(node_id)

    def summary_cluster(self) -> Dict[str, Any]:
        return self._client.get_idrac_cluster_summary()

    def available_idrac_tables(self) -> List[str]:
        return self._client.get_available_idrac_metrics()



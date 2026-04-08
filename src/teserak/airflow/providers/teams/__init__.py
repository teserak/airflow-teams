from __future__ import annotations

import packaging.version

from airflow import __version__ as airflow_version

__all__ = ["__version__"]

__version__ = "1.0.0"

if packaging.version.parse(packaging.version.parse(airflow_version).base_version) < packaging.version.parse(
    "2.11.0"
):
    raise RuntimeError(
        f"The package `teserak-airflow-providers-teams:{__version__}` needs Apache Airflow 2.11.0+"
    )

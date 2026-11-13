"""Tool for ingesting CSV/Excel role data uploads."""
import io
import json
import logging
from langchain_core.tools import tool
from role_discovery_tool import merge_records, normalize_environment, get_session_dataset

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"user_id", "role_name", "environment"}
EXPECTED_FORMAT = (
    "Expected columns: user_id, role_name, environment, functional_type (optional). "
    "Example row: USR001,SAP_EMPLOYEE_SELF_SERVICE,S4_CLOUD,Functional"
)


@tool
def file_ingestion_tool(file_content: str, file_format: str = "csv") -> str:
    """Parse and ingest a CSV or Excel role data file into the session dataset.

    Args:
        file_content: The raw file content as a string (CSV) or base64-encoded bytes (xlsx).
        file_format: File format — 'csv' or 'xlsx'.
    """
    try:
        import pandas as pd
    except ImportError:
        return json.dumps({"status": "error", "message": "pandas library not available. Install it with: pip install pandas openpyxl"})

    try:
        if file_format.lower() == "csv":
            df = pd.read_csv(io.StringIO(file_content))
        elif file_format.lower() in ("xlsx", "excel"):
            import base64
            raw_bytes = base64.b64decode(file_content)
            df = pd.read_excel(io.BytesIO(raw_bytes))
        else:
            return json.dumps({
                "status": "error",
                "message": f"Unsupported file format: '{file_format}'. Use 'csv' or 'xlsx'.",
            })

        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Validate required columns
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            return json.dumps({
                "status": "error",
                "message": f"Missing required columns: {sorted(missing)}. {EXPECTED_FORMAT}",
                "found_columns": list(df.columns),
                "missing_columns": sorted(missing),
            })

        # Remove rows with null required fields
        df = df.dropna(subset=list(REQUIRED_COLUMNS))

        records = []
        row_errors = []
        for idx, row in df.iterrows():
            env = normalize_environment(str(row["environment"]))
            records.append({
                "user_id": str(row["user_id"]).strip(),
                "role_name": str(row["role_name"]).strip(),
                "environment": env,
                "functional_type": str(row.get("functional_type", "")).strip() if "functional_type" in df.columns else "",
                "source": "file_upload",
                "source_ref": f"upload/row_{idx + 2}",
            })

        if row_errors:
            return json.dumps({
                "status": "partial_error",
                "message": "Some rows had errors.",
                "row_errors": row_errors,
            })

        added = merge_records(records)
        return json.dumps({
            "status": "success",
            "rows_processed": len(records),
            "records_added": added,
            "total_in_session": len(get_session_dataset()),
        })

    except Exception as e:
        logger.error("file_ingestion_tool error: %s", e)
        return json.dumps({"status": "error", "message": str(e)})

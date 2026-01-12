"""
Ingestion script that sends documents to Elysia API via HTTP.

This script processes documents and uploads them to the Elysia backend
using the REST API endpoint instead of direct service imports.
"""
import logging
import os
from pathlib import Path
from typing import Sequence

import requests

# Environment configuration
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
PIPELINE_DATA_DIR = Path(os.getenv("PIPELINE_DATA_DIR", "../input_files"))
ELYSIA_API_URL = os.getenv("ELYSIA_API_URL", "http://localhost:8000")
PIPELINE_USER_ID = os.getenv("PIPELINE_USER_ID", "")
PIPELINE_AUTO_PREPROCESS = os.getenv("PIPELINE_AUTO_PREPROCESS", "true").lower() == "true"
PIPELINE_AUTO_GEOCODE = os.getenv("PIPELINE_AUTO_GEOCODE", "false").lower() == "true"
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".html", ".docx", ".eml", ".mbox"}

# Configure logging with environment-driven level
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Suppress noisy libraries (keep at WARNING unless explicitly DEBUG)
if LOGGING_LEVEL != "DEBUG":
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

# API request timeout
REQUEST_TIMEOUT = 300  # 5 minutes for large file uploads


def _relative_to_data_dir(path: Path) -> str | None:
    """Get path relative to data directory."""
    try:
        return str(path.relative_to(PIPELINE_DATA_DIR))
    except ValueError:
        return None


def _collect_files(target_files: Sequence[str] | None) -> list[Path]:
    """Collect files to process from target list or data directory."""
    if target_files:
        files = [Path(p).resolve() for p in target_files]
        logger.info(f"Processing {len(files)} explicitly provided files")
        return files

    logger.info(
        "Scanning for files with extensions: " + ", ".join(sorted(SUPPORTED_EXTENSIONS))
    )

    discovered: list[Path] = []
    if not PIPELINE_DATA_DIR.exists():
        logger.warning(f"PIPELINE_DATA_DIR {PIPELINE_DATA_DIR} does not exist")
        return discovered

    for root, _, files in os.walk(PIPELINE_DATA_DIR):
        root_path = Path(root)
        if "processed" in root_path.parts:
            continue

        for filename in files:
            if Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS:
                discovered.append(root_path / filename)

    return discovered


def upload_document_to_api(file_path: Path) -> dict:
    """
    Upload a document to the Elysia API.

    Args:
        file_path: Path to the document file

    Returns:
        dict: Response from the API containing success status and document_id

    Raises:
        requests.RequestException: If the upload fails
    """
    if not PIPELINE_USER_ID:
        raise ValueError("PIPELINE_USER_ID environment variable is not set")

    # Construct the upload endpoint URL
    upload_url = f"{ELYSIA_API_URL}/documents/{PIPELINE_USER_ID}/upload"

    logger.debug(f"DEBUG: Upload target URL: {upload_url}")
    logger.debug(f"DEBUG: File path: {file_path}")
    logger.debug(f"DEBUG: File exists: {file_path.exists()}")
    logger.debug(f"DEBUG: File size: {file_path.stat().st_size if file_path.exists() else 'N/A'} bytes")

    try:
        # Prepare the multipart form data
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path.name, f, _get_content_type(file_path))
            }

            data = {
                "auto_preprocess": str(PIPELINE_AUTO_PREPROCESS).lower(),
                "auto_geocode": str(PIPELINE_AUTO_GEOCODE).lower(),
                "create_agent": "false",
            }

            logger.debug(f"Request data: {data}")

            # Make the POST request
            response = requests.post(
                upload_url,
                files=files,
                data=data,
                timeout=REQUEST_TIMEOUT
            )

            logger.debug(f"API response status: {response.status_code}")
            response.raise_for_status()

            result = response.json()
            logger.debug(f"API response: {result}")
            return result

    except requests.exceptions.Timeout:
        logger.error(f"Upload timeout for {file_path.name} after {REQUEST_TIMEOUT}s")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Upload failed for {file_path.name}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        raise


def _get_content_type(file_path: Path) -> str:
    """Get MIME type for a file based on extension."""
    extension_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".eml": "message/rfc822",
        ".mbox": "application/mbox",
    }
    return extension_map.get(file_path.suffix.lower(), "application/octet-stream")


def ingest_files(files_to_process: list[Path]) -> None:
    """
    Ingest files by uploading them to the Elysia API.

    Args:
        files_to_process: List of file paths to ingest
    """
    if not files_to_process:
        logger.info("No files found for ingestion")
        return

    successes = 0
    failures = 0

    for idx, file_path in enumerate(files_to_process, start=1):
        logger.info(f"[{idx}/{len(files_to_process)}] Processing document: {file_path.name}")

        try:
            # Check file exists and is readable
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                failures += 1
                continue

            if not file_path.is_file():
                logger.error(f"Not a file: {file_path}")
                failures += 1
                continue

            # Upload to API
            result = upload_document_to_api(file_path)

            # Check response
            if result.get("success"):
                document_id = result.get("document_id", "unknown")
                logger.info(
                    f"Successfully ingested {file_path.name} (document_id={document_id})"
                )
                successes += 1
            else:
                error = result.get("error", "unknown error")
                logger.error(f"Failed to ingest {file_path.name}: {error}")
                failures += 1

        except Exception as exc:
            failures += 1
            logger.error(f"Error ingesting {file_path.name}: {exc}", exc_info=True)

    logger.info(
        f"Ingestion completed. Successes: {successes}, Failures: {failures}"
    )


def main(target_files: Sequence[str] | None = None) -> None:
    """
    Main ingestion entry point.

    Args:
        target_files: Optional list of specific files to process.
                     If None, scans PIPELINE_DATA_DIR for supported files.
    """
    logger.info(f"Starting ingestion - Logging level: {LOGGING_LEVEL}")
    logger.info(f"PIPELINE_DATA_DIR: {PIPELINE_DATA_DIR}")
    logger.info(f"Elysia API URL: {ELYSIA_API_URL}")
    logger.info(f"User ID: {PIPELINE_USER_ID}")
    logger.info(f"Auto preprocess: {PIPELINE_AUTO_PREPROCESS}")
    logger.info(f"Auto geocode: {PIPELINE_AUTO_GEOCODE}")
    logger.debug(f"DEBUG: Target files provided: {target_files}")
    logger.debug(f"DEBUG: Request timeout: {REQUEST_TIMEOUT}s")

    files_to_process = _collect_files(target_files)
    logger.info(
        f"Found {len(files_to_process)} files to ingest"
    )

    ingest_files(files_to_process)


if __name__ == "__main__":
    main()

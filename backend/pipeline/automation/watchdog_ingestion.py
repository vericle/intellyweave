"""
Simplified watchdog for document ingestion with project based directory management.

Flow:
1. Watch input_files root directories (e.g., /input_files/ratline_example/)
2. New files appear in root → move to processing/ subdirectory
3. Ingest files from processing/
4. Move completed files to processed/
"""

import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configuration from environment
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
PIPELINE_DATA_DIR = os.getenv("PIPELINE_DATA_DIR", "../input_files")

# Configure logging with environment-driven level
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Suppress noisy libraries (keep at WARNING unless explicitly DEBUG)
if LOGGING_LEVEL != "DEBUG":
    logging.getLogger("watchdog").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

BATCH_WAIT_SECONDS = int(os.getenv("BATCH_WAIT_SECONDS", "4"))
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".html", ".docx", ".eml", ".mbox"}


# Global state
pending_files = set()
last_event_time = None


def get_projects():
    """Get list of project directories."""
    projects = []
    for item in os.listdir(PIPELINE_DATA_DIR):
        item_path = os.path.join(PIPELINE_DATA_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            projects.append(item_path)
    return projects


class DocumentEventHandler(FileSystemEventHandler):
    """Handle file system events for document ingestion."""

    def on_created(self, event):
        """Called when a file is created in project root."""
        if event.is_directory:
            return
        self._handle_file_event(event.src_path)

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        self._handle_file_event(event.src_path)

    def _handle_file_event(self, filepath):
        """Handle a file event - move to processing/ if in project root."""
        global pending_files, last_event_time

        # Check if file has supported extension
        if not any(filepath.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            return

        # Check if file exists and is complete (size > 0)
        try:
            if not os.path.exists(filepath):
                return

            file_size = os.path.getsize(filepath)
            if file_size == 0:
                logger.debug(f"Skipping empty file: {filepath}")
                return
        except Exception as e:
            logger.error(f"Error checking file {filepath}: {e}")
            return

        # Get project root and check if file is in root (not in subdirectory)
        project_root = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        # Check if this is a project directory (has processing/ subdirectory)
        processing_dir = os.path.join(project_root, "processing")
        if not os.path.exists(processing_dir):
            logger.debug(
                f"Skipping {filepath} - not in a project root (no processing/ dir found)"
            )
            return

        logger.info(
            f"New file detected in project root: {filename} ({file_size} bytes)"
        )

        # Move to processing/ subdirectory
        try:
            dest_path = os.path.join(processing_dir, filename)
            logger.debug(f"Moving {filepath} to {dest_path}")
            shutil.move(filepath, dest_path)
            logger.info(f"Moved {filename} → processing/")

            # Add to pending batch
            pending_files.add(dest_path)
            last_event_time = time.time()
            logger.debug(
                f"Added {filename} to pending batch. Total pending: {len(pending_files)}"
            )

        except Exception as e:
            logger.error(
                f"Failed to move {filename} to processing/: {e}", exc_info=True
            )


def run_ingestion(files):
    """Run ingestion pipeline for a batch of files."""
    logger.info(f"Starting ingestion for {len(files)} files")

    try:
        sys.path.insert(0, "/app/pipeline/ingestion")
        from ingest_elastic_weaviate import main as ingest_main

        logger.info("Running Elasticsearch + Weaviate ingestion...")
        ingest_main(files)
        logger.info("Ingestion completed successfully")
        return True

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        return False


def move_to_processed(files):
    """Move successfully processed files to processed/ directory."""
    for filepath in files:
        try:
            if not os.path.exists(filepath):
                continue

            # Get project root and processed directory
            project_root = os.path.dirname(
                os.path.dirname(filepath)
            )  # Go up from processing/
            processed_dir = os.path.join(project_root, "processed")

            if not os.path.exists(processed_dir):
                logger.error(f"Processed directory not found: {processed_dir}")
                continue

            filename = os.path.basename(filepath)
            dest_path = os.path.join(processed_dir, filename)

            # Handle duplicates by appending timestamp
            if os.path.exists(dest_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(processed_dir, f"{name}_{timestamp}{ext}")

            shutil.move(filepath, dest_path)
            logger.info(f"Moved {filename} → processed/")

        except Exception as e:
            logger.error(f"Failed to move {filepath}: {e}")


def process_batch():
    """Process pending files batch."""
    global pending_files, last_event_time

    if not pending_files:
        return

    # Wait for batch to settle
    if last_event_time is None:
        return

    time_since_last_event = time.time() - last_event_time
    if time_since_last_event < BATCH_WAIT_SECONDS:
        logger.debug(
            f"Waiting for batch to settle... ({int(time_since_last_event)}/{BATCH_WAIT_SECONDS}s)"
        )
        return

    # Process the batch
    files_to_process = list(pending_files)
    pending_files = set()
    last_event_time = None

    logger.info(
        f"Processing batch of {len(files_to_process)} files: {[os.path.basename(f) for f in files_to_process]}"
    )

    # Step 1: Ingest to Elasticsearch + Weaviate
    if not run_ingestion(files_to_process):
        logger.error("Ingestion failed, skipping Newsleak preprocessing")
        return

    # Step 2: Move files to processed
    move_to_processed(files_to_process)

    logger.info("Pipeline completed successfully!")


def scan_processing_directories():
    """Scan existing files in all project processing/ directories on startup."""
    projects = get_projects()

    for project_path in projects:
        processing_dir = os.path.join(project_path, "processing")
        if not os.path.exists(processing_dir):
            continue

        project_name = os.path.basename(project_path)
        logger.info(f"Scanning {project_name}/processing/ for existing files...")

        for root, _, files in os.walk(processing_dir):
            for f in files:
                if any(f.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                    full_path = os.path.join(root, f)
                    global pending_files, last_event_time
                    pending_files.add(full_path)
                    last_event_time = time.time()

    if pending_files:
        logger.info(
            f"Found {len(pending_files)} existing files in processing/ directories"
        )
    else:
        logger.info("No existing files found")


def main():
    """Main watchdog loop."""
    logger.info("=" * 80)
    logger.info("COLLECTION-BASED DOCUMENT INGESTION PIPELINE")
    logger.info("=" * 80)
    logger.info(f"Logging level: {LOGGING_LEVEL}")
    logger.info(f"Data directory: {PIPELINE_DATA_DIR}")
    logger.info(f"Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}")
    logger.info(f"Batch wait time: {BATCH_WAIT_SECONDS}s")
    logger.debug(f"DEBUG: Resolved data dir exists: {os.path.exists(PIPELINE_DATA_DIR)}")
    logger.debug(f"DEBUG: Resolved data dir contents: {os.listdir(PIPELINE_DATA_DIR) if os.path.exists(PIPELINE_DATA_DIR) else 'N/A'}")
    logger.info("=" * 80)

    # Wait for services to be ready
    logger.info("Waiting for services to be ready...")
    time.sleep(15)

    # Get projects and log them
    projects = get_projects()
    logger.info(f"Found {len(projects)} projects:")
    for project in projects:
        project_name = os.path.basename(project)
        logger.info(f"  - {project_name}")
    # Scan for existing files in processing/ directories
    scan_processing_directories()

    # Set up watchdog observers for each project root
    event_handler = DocumentEventHandler()
    observer = Observer()

    for project_path in projects:
        # Only watch if processing/ subdirectory exists
        processing_dir = os.path.join(project_path, "processing")
        if os.path.exists(processing_dir):
            observer.schedule(event_handler, project_path, recursive=False)
            project_name = os.path.basename(project_path)
            logger.info(f"Watching: {project_name}/ (root only)")

    observer.start()
    logger.info("Watchdog started. Monitoring project directories...")

    try:
        while True:
            # Check for pending batches
            process_batch()
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("Shutting down watchdog...")
        observer.stop()

    observer.join()
    logger.info("Watchdog stopped")


if __name__ == "__main__":
    main()

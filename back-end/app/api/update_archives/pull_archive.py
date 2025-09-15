from fastapi import APIRouter, UploadFile, File, Depends, Body, Query
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiofiles, tempfile, zipfile, os, shutil, asyncio, logging
import datetime
import re
import tempfile, zipfile, os, shutil, asyncio, logging
import datetime

router = APIRouter(prefix="/archives", tags=["archives"])
logger = logging.getLogger("uvicorn")

CHUNK_SIZE = 1024 * 1024  # 1 MB chunks

# Define the archive directory path
ARCHIVE_PATH = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/.archive")

@router.get("/list")
async def list_archive_files(
    include_details: bool = Query(True), 
    filter_ext: Optional[str] = Query(None),
    recursive: bool = Query(True),
    flat_structure: bool = Query(True)
):
    """
    List all files and directories in the archive directory
    
    Args:
        include_details: Whether to include file details (size, modified date, etc.)
        filter_ext: Optional file extension filter (e.g., 'update' for *.update files)
        recursive: Whether to search recursively in subdirectories
        flat_structure: Whether to return a flat list of files or maintain directory structure
    """
    try:
        # Create directory if it doesn't exist
        ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
        
        # Initialize response structure
        response = {
            "directory": str(ARCHIVE_PATH),
            "items": []
        }
        
        # Function to process a file
        def process_file(file_path, rel_path):
            # Skip if filtering by extension and this doesn't match
            if filter_ext and file_path.suffix.lower() != f".{filter_ext.lower()}":
                return None
                
            # Basic item info
            item_info = {
                "name": file_path.name,
                "path": str(rel_path),
                "is_directory": False,
                "parent_dir": str(file_path.parent.name)
            }
            
            # Add additional file details if requested
            if include_details:
                try:
                    stats = file_path.stat()
                    item_info.update({
                        "size": stats.st_size,
                        "size_human": format_size(stats.st_size),
                        "modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        "created": datetime.datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    })
                except Exception as e:
                    logger.error(f"Error getting details for {file_path}: {str(e)}")
                    item_info["error"] = f"Failed to get details: {str(e)}"
                    
            return item_info
        
        # Function to process all files in a directory recursively
        def scan_directory(dir_path, results, current_rel_path=""):
            # Process all items in the directory
            for item_path in dir_path.iterdir():
                rel_path = Path(current_rel_path) / item_path.name
                
                if item_path.is_file():
                    item_info = process_file(item_path, rel_path)
                    if item_info:
                        results.append(item_info)
                elif item_path.is_dir() and recursive:
                    # Either add directory entry or just scan its contents
                    if not flat_structure:
                        dir_info = {
                            "name": item_path.name,
                            "path": str(rel_path),
                            "is_directory": True
                        }
                        
                        if include_details:
                            try:
                                stats = item_path.stat()
                                dir_info.update({
                                    "modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
                                    "created": datetime.datetime.fromtimestamp(stats.st_ctime).isoformat(),
                                })
                                dir_info["contains"] = len(list(item_path.iterdir()))
                            except Exception as e:
                                logger.error(f"Error getting details for {item_path}: {str(e)}")
                                dir_info["error"] = f"Failed to get details: {str(e)}"
                                
                        results.append(dir_info)
                    
                    # Scan subdirectory recursively
                    scan_directory(item_path, results, str(rel_path))
        
        # Start the recursive scan
        scan_directory(ARCHIVE_PATH, response["items"])
        
        # Extract build info from update filenames when possible
        for item in response["items"]:
            if not item["is_directory"] and item["name"].lower().endswith(".update"):
                # Try to extract version and build type from filename
                try:
                    name = item["name"]
                    # Extract version (format: V0.1.38D)
                    version_match = re.search(r'V(\d+\.\d+\.\d+[A-Z]?)', name)
                    if version_match:
                        item["version"] = version_match.group(1)
                        
                        # Determine if development or public release
                        item["release_type"] = "development" if "D" in name or "D" in item["version"] else "public"
                    
                    # Extract date (format: 20250806)
                    date_match = re.search(r'_(\d{8})\.', name)
                    if date_match:
                        date_str = date_match.group(1)
                        try:
                            year = date_str[0:4]
                            month = date_str[4:6]
                            day = date_str[6:8]
                            date_obj = datetime.date(int(year), int(month), int(day))
                            item["build_date"] = date_obj.isoformat()
                            
                            # Add a formatted date string
                            item["build_date_formatted"] = date_obj.strftime("%b %d, %Y")
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Could not parse date from {date_str}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Error extracting metadata from filename {item['name']}: {str(e)}")
        
        # Sort items: by date (newest first), then by name
        response["items"].sort(
            key=lambda x: (
                # Sort by build date (newest first) if available
                datetime.datetime.fromisoformat(x.get("build_date", "1970-01-01")).timestamp() * -1 
                if "build_date" in x else 0,
                # Then by name
                x["name"].lower()
            )
        )
        
        return response
    except Exception as e:
        logger.error(f"Error listing archive files: {str(e)}")
        return {"error": f"Failed to list archive files: {str(e)}"}


@router.get("/download/{file_path:path}")
async def download_archive_file(file_path: str):
    """
    Download a specific file from the archive directory
    
    Args:
        file_path: Relative path to the file within the archive directory
    """
    try:
        # Construct absolute path and normalize it
        absolute_path = (ARCHIVE_PATH / file_path).resolve()
        
        # Security check - make sure the resolved path is still within the archive directory
        if not str(absolute_path).startswith(str(ARCHIVE_PATH)):
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied: attempting to access file outside archive directory"}
            )
        
        # Check if file exists
        if not absolute_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": f"File not found: {file_path}"}
            )
            
        if not absolute_path.is_file():
            return JSONResponse(
                status_code=400,
                content={"error": f"Path is not a file: {file_path}"}
            )
            
        # Return the file
        return FileResponse(
            path=absolute_path,
            filename=absolute_path.name,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )


def format_size(size_bytes):
    """Format file size in a human-readable format"""
    if size_bytes < 0:
        return "Invalid size"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
        
    return f"{size_bytes:.2f} {units[unit_index]}"


async def clear_archive_files():
    """Clear all DEB files from the debs directory"""
    try:
        # Create directory if it doesn't exist
        ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
        
        # Count existing files
        existing_files = list(ARCHIVE_PATH.glob("*.deb"))
        count = len(existing_files)
        
        # Clear existing debs
        for deb in existing_files:
            logger.info(f"Deleting file: {deb}")
            deb.unlink(missing_ok=True)
        
        logger.info(f"Cleared {count} files from {ARCHIVE_PATH}")
        return {"message": f"Cleared {count} DEB files", "count": count}
    except Exception as e:
        logger.error(f"Error clearing DEB files: {str(e)}")
        return {"error": f"Failed to clear DEB files: {str(e)}", "count": 0}
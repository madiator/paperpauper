"""Parses PDFs from URLs into markdown using Aryn.

You can use other parsers as well.
"""
from typing import List, Dict
from pathlib import Path
import hashlib
import json
import requests
from aryn_sdk.partition import partition_file


def get_pdf_markdown(urls: List[str], cache_dir: str = ".cache") -> List[Dict[str, str]]:
    """Downloads PDFs from URLs, converts them to markdown, and caches the results.

    Args:
        urls: List of URLs pointing to PDF files.
        cache_dir: Directory to store cached markdown files. Defaults to ".cache".
        
    Returns:
        Dictionary mapping URLs to their markdown content.
    """
    # Create cache directory if it doesn't exist
    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)
    
    results = []
    
    for url in urls:
        # Create hash of URL for cache filename
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        cache_file = cache_path / f"{url_hash}.json"
        
        # Check if cached version exists
        if cache_file.exists():
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
                results.append({
                    "url": url,
                    "markdown": cached_data["markdown"]
                })
            continue
            
        # Download PDF if not cached
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Convert PDF to markdown
            markdown = partition_file(response.content, output_format="markdown")
            
            # Cache the results
            with open(cache_file, "w") as f:
                json.dump({
                    "url": url,
                    "markdown": markdown
                }, f)
                
            results.append({
                "url": url,
                "markdown": markdown
            })
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            results.append({
                "url": url,
                "markdown": ""
            })
            
    return results

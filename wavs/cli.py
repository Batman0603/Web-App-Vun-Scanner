import argparse
import sys
from typing import Any
import time

import httpx

from asicart import color_text

API_GATEWAY_URL = "http://localhost:8000"


def display_banner() -> None:
    banner = r"""
 __          __        __      __   _____ 
 \ \        / /  /\    \ \    / /  / ____|
  \ \  /\  / /  /  \    \ \  / /  | (___  
   \ \/  \/ /  / /\ \    \ \/ /    \___ \ 
    \  /\  /  / ____ \    \  /     ____) |
     \/  \/  /_/    \_\    \/     |_____/ 
    """
    print(color_text(banner, "magenta"))
    print(color_text("Web Application Vulnerability Scanner", "cyan"))
    print(color_text("Run the full pipeline: crawler -> attack-surface -> payload -> detection -> report", "yellow"))
    print()


def prompt_for_target() -> tuple[str, int]:
    target = input(color_text("Enter target URL: ", "green")).strip()
    if not target:
        print(color_text("Target URL cannot be empty.", "red"))
        sys.exit(1)

    depth_text = input(color_text("Enter crawl depth [2]: ", "green")).strip() or "2"
    try:
        depth = int(depth_text)
    except ValueError:
        print(color_text("Depth must be an integer.", "red"))
        sys.exit(1)

    return target, depth


def initiate_scan(target: str, depth: int) -> str:
    url = f"{API_GATEWAY_URL}/scan"
    payload = {"url": target, "depth": depth}

    try:
        # Set timeout to None to ensure we wait for the scan_id even if the gateway is slow
        with httpx.Client(timeout=None) as client:
            response = client.post(url, json=payload)
            print(response.text)
            response.raise_for_status()
            return response.json()["scan_id"]
    except httpx.ConnectError:
        print(color_text(f"Could not connect to API Gateway at {API_GATEWAY_URL}. Is it running?", "red"))
        sys.exit(1)


def poll_scan_status(scan_id: str) -> Any:
    status_url = f"{API_GATEWAY_URL}/scan/{scan_id}"
    
    last_status_message = ""
    retry_count = 0
    max_retries = 10
    
    while True:
        try: # Removed timeout to wait indefinitely for status updates
            with httpx.Client(timeout=None) as client:
                response = client.get(status_url)
                response.raise_for_status()
                scan_status = response.json()
            
            retry_count = 0  # Reset retry count on success

            status = scan_status.get("status", "unknown")
            stage = scan_status.get("stage", "N/A")
            progress = scan_status.get("progress", 0)
            
            current_status_message = f"Current status: {status.capitalize()}, Stage: {stage.replace('_', ' ').title()}, Progress: {progress}%"
            
            if current_status_message != last_status_message:
                print(color_text(current_status_message, "yellow"))
                last_status_message = current_status_message

            if status == "completed":
                print(color_text("\nScan completed successfully!", "green"))
                return scan_status
            elif status == "failed":
                error_message = scan_status.get("error", "An unknown error occurred.")
                print(color_text(f"\nScan failed: {error_message}", "red"))
                sys.exit(1)
            
            time.sleep(2) # Poll every 2 seconds

        except httpx.RequestError as exc:
            print(color_text(f"Polling failed: {exc}. Retrying...", "red"))
            time.sleep(5) # Longer wait on network error
        except httpx.HTTPStatusError as exc:
            print(color_text(f"API Gateway returned error ({exc.response.status_code}): {exc.response.text}. Exiting.", "red"))
            sys.exit(1)
        except Exception as e:
            retry_count += 1

            if retry_count >= max_retries:
                print(color_text("Too many polling failures", "red"))
                sys.exit(1)

            print(color_text(f"Temporary polling error: {e}", "yellow"))
            time.sleep(2)
            continue


def main() -> None:
    parser = argparse.ArgumentParser(prog="WAVS", description="WAVS CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Run the full WAVS scan pipeline")
    subparsers.add_parser("version", help="Show WAVS version")

    args = parser.parse_args()

    if args.command == "version":
        print("WAVS version 0.1.0")
        return

    if args.command != "run":
        parser.print_help()
        return

    display_banner()
    target, depth = prompt_for_target()

    print(color_text(f"Initiating scan for {target} at depth {depth}...", "blue"))
    try:
        scan_id = initiate_scan(target, depth)
        print(color_text(f"Scan initiated successfully! Scan ID: {scan_id}", "green"))
        print(color_text(f"Polling for scan status...", "magenta"))
        
        final_results = poll_scan_status(scan_id)
        
        # Display final summary
        print(color_text("\nScan complete! Summary:\n", "green"))
        print(color_text(f"Target: {final_results.get('url')}", "cyan"))
        print(color_text(f"Depth: {final_results.get('depth')}", "cyan"))
        
        crawler_results = final_results.get('crawler_results', {})
        detection_results = final_results.get('detection_results', {})
        
        print(color_text(f"Total scanned pages: {crawler_results.get('total_pages', 'N/A')}", "yellow"))
        print(color_text(f"Vulnerabilities found: {detection_results.get('vulnerabilities_found', 0)}", "yellow"))
        
        print(color_text("\nFinal Report:", "green"))
        import json
        # Display only the report data
        print(json.dumps(final_results.get('report', {}), indent=2))
    except httpx.RequestError as exc:
        print(color_text(f"Request failed: {exc}", "red"))
        sys.exit(1)
    except httpx.HTTPStatusError as exc:
        print(color_text(f"Service returned error ({exc.response.status_code}): {exc.response.text}", "red"))
        sys.exit(1)

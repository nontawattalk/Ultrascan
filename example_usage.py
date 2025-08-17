#!/usr/bin/env python3
"""
Ultra-Fast Port Scanner - Integration Examples
This file shows how to integrate the scanner into your own tools
"""

import subprocess
import json
import sys
from pathlib import Path

def run_scanner(target, ports="1-1000", threads=1000, timeout=0.1, export_format=None):
    """
    Run Ultra-Fast Port Scanner and return results
    
    Args:
        target (str): Target IP or hostname
        ports (str): Port range (e.g., "1-65535", "80,443,8080")
        threads (int): Number of threads
        timeout (float): Socket timeout
        export_format (str): Export format ("json" or "nmap")
    
    Returns:
        dict: Scan results
    """
    cmd = [
        "python3", "ultra_scanner.py",
        target,
        "-p", ports,
        "-t", str(threads),
        "--timeout", str(timeout),
        "--no-progress"
    ]
    
    if export_format:
        cmd.extend(["--export", export_format])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse output to extract results
        lines = result.stdout.strip().split('\n')
        
        # Find the results section
        results = {
            'target': target,
            'success': True,
            'open_ports': [],
            'scan_time': 0,
            'ports_per_second': 0
        }
        
        for line in lines:
            if 'Open ports:' in line:
                # Extract open ports from the next line
                next_idx = lines.index(line) + 1
                if next_idx < len(lines):
                    port_line = lines[next_idx].strip()
                    if port_line:
                        results['open_ports'] = [int(p) for p in port_line.split()]
            elif 'Scan time:' in line:
                results['scan_time'] = float(line.split(':')[1].strip().split()[0])
            elif 'Rate:' in line:
                results['ports_per_second'] = float(line.split(':')[1].strip().split()[0])
        
        return results
        
    except subprocess.CalledProcessError as e:
        return {
            'target': target,
            'success': False,
            'error': e.stderr,
            'return_code': e.returncode
        }

def scan_multiple_targets(targets, ports="1-1000"):
    """
    Scan multiple targets and aggregate results
    
    Args:
        targets (list): List of targets to scan
        ports (str): Port range to scan
    
    Returns:
        list: List of scan results
    """
    results = []
    
    print(f"Scanning {len(targets)} targets...")
    
    for i, target in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] Scanning {target}...")
        
        result = run_scanner(target, ports=ports, threads=500, timeout=0.2)
        results.append(result)
        
        if result['success']:
            print(f"  ✓ Found {len(result['open_ports'])} open ports in {result['scan_time']:.1f}s")
        else:
            print(f"  ✗ Scan failed: {result.get('error', 'Unknown error')}")
    
    return results

def generate_report(results, output_file="scan_report.html"):
    """
    Generate HTML report from scan results
    
    Args:
        results (list): List of scan results
        output_file (str): Output HTML file path
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultra-Fast Port Scanner Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
            .target { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
            .success { border-left: 4px solid #27ae60; }
            .failure { border-left: 4px solid #e74c3c; }
            .ports { background: #ecf0f1; padding: 10px; border-radius: 3px; font-family: monospace; }
            .stats { background: #3498db; color: white; padding: 10px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Ultra-Fast Port Scanner Report</h1>
            <p>Generated on: {timestamp}</p>
        </div>
        
        <div class="stats">
            <h2>Summary Statistics</h2>
            <p><strong>Total Targets:</strong> {total_targets}</p>
            <p><strong>Successful Scans:</strong> {successful_scans}</p>
            <p><strong>Total Open Ports:</strong> {total_open_ports}</p>
            <p><strong>Average Scan Time:</strong> {avg_scan_time:.2f}s</p>
        </div>
        
        {target_results}
    </body>
    </html>
    """
    
    from datetime import datetime
    
    # Calculate statistics
    successful = [r for r in results if r['success']]
    total_open_ports = sum(len(r.get('open_ports', [])) for r in successful)
    avg_scan_time = sum(r.get('scan_time', 0) for r in successful) / len(successful) if successful else 0
    
    # Generate target results HTML
    target_html = ""
    for result in results:
        if result['success']:
            ports_str = ', '.join(map(str, result['open_ports'])) if result['open_ports'] else 'None'
            target_html += f"""
            <div class="target success">
                <h3>✓ {result['target']}</h3>
                <p><strong>Open Ports:</strong> {len(result['open_ports'])}</p>
                <div class="ports">{ports_str}</div>
                <p><strong>Scan Time:</strong> {result['scan_time']:.2f}s | 
                   <strong>Rate:</strong> {result['ports_per_second']:.0f} ports/sec</p>
            </div>
            """
        else:
            target_html += f"""
            <div class="target failure">
                <h3>✗ {result['target']}</h3>
                <p><strong>Error:</strong> {result.get('error', 'Scan failed')}</p>
            </div>
            """
    
    # Fill template
    html_content = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_targets=len(results),
        successful_scans=len(successful),
        total_open_ports=total_open_ports,
        avg_scan_time=avg_scan_time,
        target_results=target_html
    )
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Report generated: {output_file}")

def scan_network_range(network, common_ports_only=True):
    """
    Scan a network range (e.g., 192.168.1.0/24)
    
    Args:
        network (str): Network in CIDR notation
        common_ports_only (bool): Whether to scan only common ports
    
    Returns:
        dict: Network scan results
    """
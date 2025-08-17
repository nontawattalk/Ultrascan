#!/usr/bin/env python3
"""
Ultra-Fast Port Scanner
A high-performance port scanner with adaptive intelligence
GitHub: https://github.com/yourusername/ultra-fast-port-scanner
"""

import socket
import threading
import time
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import signal
from collections import deque
import json

class UltraPortScanner:
    def __init__(self, target, threads=1000, timeout=0.1, chunk_size=1000):
        self.target = target
        self.threads = threads
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.open_ports = []
        self.closed_ports = []
        self.results_lock = threading.Lock()
        self.start_time = None
        self.ports_scanned = 0
        self.total_ports = 0
        
        # Adaptive parameters
        self.adaptive_timeout = timeout
        self.response_times = deque(maxlen=100)
        self.consecutive_failures = 0
        
    def resolve_target(self):
        """Resolve hostname to IP"""
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror:
            print(f"Error: Cannot resolve hostname {self.target}")
            sys.exit(1)
    
    def scan_port(self, ip, port):
        """Scan a single port with adaptive timeout"""
        start_time = time.time()
        
        try:
            # Create socket with optimized settings
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.adaptive_timeout)
            
            # Enable socket reuse for faster scanning
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            result = sock.connect_ex((ip, port))
            sock.close()
            
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            with self.results_lock:
                self.ports_scanned += 1
                if result == 0:
                    self.open_ports.append(port)
                    self.consecutive_failures = 0
                    return True
                else:
                    self.consecutive_failures += 1
                    return False
                    
        except Exception:
            with self.results_lock:
                self.ports_scanned += 1
                self.consecutive_failures += 1
            return False
    
    def adaptive_adjust(self):
        """Dynamically adjust scanning parameters based on network conditions"""
        if len(self.response_times) > 10:
            avg_response = sum(self.response_times) / len(self.response_times)
            
            # Adjust timeout based on average response time
            if avg_response < 0.05:  # Very fast network
                self.adaptive_timeout = max(0.05, avg_response * 2)
            elif avg_response > 0.5:  # Slow network
                self.adaptive_timeout = min(2.0, avg_response * 1.5)
            
            # Reduce threads if too many consecutive failures
            if self.consecutive_failures > 50:
                self.threads = max(100, self.threads // 2)
                self.consecutive_failures = 0
    
    def scan_port_range_chunk(self, ip, port_chunk):
        """Scan a chunk of ports"""
        chunk_results = []
        for port in port_chunk:
            if self.scan_port(ip, port):
                chunk_results.append(port)
        return chunk_results
    
    def progress_display(self):
        """Display real-time scanning progress"""
        while self.ports_scanned < self.total_ports:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                rate = self.ports_scanned / elapsed
                progress = (self.ports_scanned / self.total_ports) * 100
                eta = (self.total_ports - self.ports_scanned) / rate if rate > 0 else 0
                
                print(f"\rProgress: {progress:.1f}% | "
                      f"Scanned: {self.ports_scanned}/{self.total_ports} | "
                      f"Rate: {rate:.0f} ports/sec | "
                      f"ETA: {eta:.0f}s | "
                      f"Open: {len(self.open_ports)} | "
                      f"Timeout: {self.adaptive_timeout:.2f}s", 
                      end='', flush=True)
            time.sleep(0.1)
    
    def scan_ports(self, start_port=1, end_port=65535, show_progress=True):
        """Main scanning function with ultra-high performance optimizations"""
        ip = self.resolve_target()
        print(f"Scanning {self.target} ({ip}) ports {start_port}-{end_port}")
        print(f"Using {self.threads} threads with {self.timeout}s timeout")
        print("-" * 60)
        
        # Prepare port ranges
        ports = list(range(start_port, end_port + 1))
        self.total_ports = len(ports)
        
        # Split ports into chunks for better thread management
        port_chunks = [ports[i:i + self.chunk_size] 
                      for i in range(0, len(ports), self.chunk_size)]
        
        self.start_time = time.time()
        
        # Start progress display thread
        if show_progress:
            progress_thread = threading.Thread(target=self.progress_display, daemon=True)
            progress_thread.start()
        
        # Use ThreadPoolExecutor for optimal thread management
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit all port chunks
            future_to_chunk = {
                executor.submit(self.scan_port_range_chunk, ip, chunk): chunk 
                for chunk in port_chunks
            }
            
            # Process completed chunks and adapt parameters
            for future in as_completed(future_to_chunk):
                try:
                    chunk_results = future.result()
                    # Adaptive adjustment every few chunks
                    if len(future_to_chunk) % 10 == 0:
                        self.adaptive_adjust()
                except Exception as e:
                    print(f"Error in chunk processing: {e}")
        
        elapsed_time = time.time() - self.start_time
        
        if show_progress:
            print()  # New line after progress
        
        return self.generate_results(elapsed_time)
    
    def generate_results(self, elapsed_time):
        """Generate and display scan results"""
        self.open_ports.sort()
        
        results = {
            'target': self.target,
            'total_ports_scanned': self.total_ports,
            'open_ports': self.open_ports,
            'open_count': len(self.open_ports),
            'scan_time': round(elapsed_time, 2),
            'ports_per_second': round(self.total_ports / elapsed_time, 2),
            'threads_used': self.threads,
            'final_timeout': round(self.adaptive_timeout, 3)
        }
        
        print(f"\n{'='*60}")
        print(f"SCAN COMPLETE - Ultra-Fast Port Scanner")
        print(f"{'='*60}")
        print(f"Target: {self.target}")
        print(f"Ports scanned: {self.total_ports}")
        print(f"Open ports found: {len(self.open_ports)}")
        print(f"Scan time: {elapsed_time:.2f} seconds")
        print(f"Rate: {self.total_ports/elapsed_time:.0f} ports/second")
        print(f"Threads used: {self.threads}")
        print(f"Adaptive timeout: {self.adaptive_timeout:.3f}s")
        
        if self.open_ports:
            print(f"\nOpen ports:")
            # Display in rows of 10 for readability
            for i in range(0, len(self.open_ports), 10):
                port_row = self.open_ports[i:i+10]
                print(" ".join(f"{port:>5}" for port in port_row))
        else:
            print("\nNo open ports found.")
        
        return results
    
    def export_results(self, results, format='json', filename=None):
        """Export results to various formats"""
        if not filename:
            timestamp = int(time.time())
            filename = f"scan_results_{self.target}_{timestamp}.{format}"
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
        elif format == 'nmap':
            # Export in nmap-compatible format
            with open(filename, 'w') as f:
                f.write(f"# Nmap scan results for {self.target}\n")
                f.write(f"# Scanned {results['total_ports_scanned']} ports in {results['scan_time']}s\n")
                for port in results['open_ports']:
                    f.write(f"{port}/tcp open\n")
        
        print(f"Results exported to: {filename}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nScan interrupted by user")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Ultra-Fast Port Scanner - Competing with RustScan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scanme.nmap.org                    # Scan top 1000 ports
  %(prog)s 192.168.1.1 -p 1-65535             # Scan all ports
  %(prog)s example.com -t 2000 --timeout 0.05 # Ultra-fast scan
  %(prog)s target.com -p 80,443,8080          # Scan specific ports
        """
    )
    
    parser.add_argument('target', help='Target IP address or hostname')
    parser.add_argument('-p', '--ports', default='1-1000', 
                       help='Port range (e.g., 1-1000, 1-65535) or specific ports (80,443,8080)')
    parser.add_argument('-t', '--threads', type=int, default=1000,
                       help='Number of threads (default: 1000)')
    parser.add_argument('--timeout', type=float, default=0.1,
                       help='Socket timeout in seconds (default: 0.1)')
    parser.add_argument('--chunk-size', type=int, default=1000,
                       help='Port chunk size for thread batching (default: 1000)')
    parser.add_argument('--export', choices=['json', 'nmap'], 
                       help='Export results format')
    parser.add_argument('--no-progress', action='store_true',
                       help='Disable progress display')
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse port specification
    if '-' in args.ports:
        start_port, end_port = map(int, args.ports.split('-'))
    elif ',' in args.ports:
        # Handle specific ports
        port_list = [int(p.strip()) for p in args.ports.split(',')]
        start_port, end_port = min(port_list), max(port_list)
        print("Note: Scanning range from min to max port specified")
    else:
        start_port = end_port = int(args.ports)
    
    # Validate inputs
    if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
        print("Error: Port numbers must be between 1 and 65535")
        sys.exit(1)
    
    if start_port > end_port:
        print("Error: Start port must be less than or equal to end port")
        sys.exit(1)
    
    # Initialize and run scanner
    scanner = UltraPortScanner(
        target=args.target,
        threads=args.threads,
        timeout=args.timeout,
        chunk_size=args.chunk_size
    )
    
    try:
        results = scanner.scan_ports(
            start_port=start_port, 
            end_port=end_port,
            show_progress=not args.no_progress
        )
        
        # Export results if requested
        if args.export:
            scanner.export_results(results, args.export)
            
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
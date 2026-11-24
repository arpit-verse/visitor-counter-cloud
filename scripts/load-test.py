"""
HPA Load Generator for visitor-counter-cloud
Targets the /stress endpoint which performs CPU-intensive SHA-256 hashing.
The /stress endpoint is bounded at STRESS_DURATION_S seconds (default 2s) per call,
ensuring each request consumes real CPU time inside the container.
"""
import argparse
import threading
import time
import urllib.request
import urllib.error

def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"Error: {e}"

def worker(url, stop_time, stats, lock):
    while time.time() < stop_time:
        res = fetch(url)
        with lock:
            stats["total"] += 1
            if res != 200:
                stats["errors"] += 1

def run_load(target_url, concurrency, duration_sec):
    print(f"=== HPA Load Generator ===")
    print(f"Target URL : {target_url}")
    print(f"Workers    : {concurrency}")
    print(f"Duration   : {duration_sec}s")
    print(f"Note       : Each /stress request burns CPU for ~2s inside the container")
    print()

    stop_time = time.time() + duration_sec
    stats = {"total": 0, "errors": 0}
    lock = threading.Lock()

    threads = []
    for _ in range(concurrency):
        t = threading.Thread(target=worker, args=(target_url, stop_time, stats, lock), daemon=True)
        t.start()
        threads.append(t)

    start_time = time.time()

    while time.time() < stop_time:
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        with lock:
            total = stats["total"]
            errs = stats["errors"]
        rps = total / max(elapsed, 1)
        print(f"[{elapsed:3d}s / {duration_sec}s] Sent: {total:5d} | Errors: {errs:3d} | RPS: {rps:.1f}")

    for t in threads:
        t.join(timeout=2.0)

    total_time = time.time() - start_time
    avg_rps = stats["total"] / total_time if total_time > 0 else 0
    print()
    print(f"=== Load Test Complete ===")
    print(f"Duration       : {total_time:.1f}s")
    print(f"Total Requests : {stats['total']}")
    print(f"Errors         : {stats['errors']}")
    print(f"Average RPS    : {avg_rps:.1f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HPA CPU Load Generator")
    parser.add_argument("--url", default="http://localhost:30080/stress",
                        help="Target endpoint (default: /stress for CPU load)")
    parser.add_argument("--workers", type=int, default=12,
                        help="Concurrent workers (default: 12)")
    parser.add_argument("--duration", type=int, default=120,
                        help="Test duration in seconds (default: 120)")
    args = parser.parse_args()

    run_load(args.url, args.workers, args.duration)

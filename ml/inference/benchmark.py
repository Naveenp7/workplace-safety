import argparse
import time
import numpy as np
import psutil
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--size", type=int, default=640)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--frames", type=int, default=100)
    args = parser.parse_args()
    
    model = YOLO(args.model)
    
    dummy_image = np.random.randint(0, 255, (args.size, args.size, 3), dtype=np.uint8)
    
    print(f"Warming up ({args.device})...")
    for _ in range(5):
        model(dummy_image, device=args.device, verbose=False)
        
    print(f"Benchmarking on {args.frames} frames...")
    latencies = []
    
    for _ in range(args.frames):
        start = time.time()
        model(dummy_image, device=args.device, verbose=False)
        latencies.append((time.time() - start) * 1000)
        
    avg_latency = np.mean(latencies)
    min_lat = np.min(latencies)
    max_lat = np.max(latencies)
    p95_lat = np.percentile(latencies, 95)
    
    mem_usage = psutil.Process().memory_info().rss / (1024 * 1024)
    
    print("\nBenchmark Results:")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"Min Latency: {min_lat:.2f} ms")
    print(f"Max Latency: {max_lat:.2f} ms")
    print(f"P95 Latency: {p95_lat:.2f} ms")
    print(f"Estimated FPS: {1000/avg_latency:.2f}")
    print(f"Memory Usage: {mem_usage:.2f} MB")

if __name__ == "__main__":
    main()

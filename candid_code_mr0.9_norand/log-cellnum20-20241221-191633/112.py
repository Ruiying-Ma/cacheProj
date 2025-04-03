# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
FAULT_TOLERANCE_THRESHOLD = 0.1
BASE_ACCESS_FREQUENCY = 1
BASE_RECENCY = 0
BASE_FAULT_TOLERANCE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a partitioned metadata structure where each partition corresponds to a different type of workload pattern (e.g., read-heavy, write-heavy). Each partition tracks access frequency, recency, and a fault tolerance score indicating the impact of eviction errors.
metadata = {
    'read-heavy': defaultdict(lambda: {'access_freq': BASE_ACCESS_FREQUENCY, 'recency': BASE_RECENCY, 'fault_tolerance': BASE_FAULT_TOLERANCE}),
    'write-heavy': defaultdict(lambda: {'access_freq': BASE_ACCESS_FREQUENCY, 'recency': BASE_RECENCY, 'fault_tolerance': BASE_FAULT_TOLERANCE})
}

def detect_workload_pattern(obj):
    # Placeholder function to determine workload pattern
    # For simplicity, assume all objects are read-heavy
    return 'read-heavy'

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    workload_pattern = detect_workload_pattern(obj)
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[workload_pattern][key]
        score = meta['access_freq'] + meta['recency']
        
        if score < min_score and meta['fault_tolerance'] > FAULT_TOLERANCE_THRESHOLD:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    workload_pattern = detect_workload_pattern(obj)
    meta = metadata[workload_pattern][obj.key]
    meta['access_freq'] += 1
    meta['recency'] = cache_snapshot.access_count
    meta['fault_tolerance'] += 0.01  # Slightly adjust fault tolerance

def update_after_insert(cache_snapshot, obj):
    # Your code below
    workload_pattern = detect_workload_pattern(obj)
    metadata[workload_pattern][obj.key] = {
        'access_freq': BASE_ACCESS_FREQUENCY,
        'recency': cache_snapshot.access_count,
        'fault_tolerance': BASE_FAULT_TOLERANCE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    workload_pattern = detect_workload_pattern(evicted_obj)
    for key, meta in metadata[workload_pattern].items():
        if key != evicted_obj.key:
            meta['fault_tolerance'] = max(FAULT_TOLERANCE_THRESHOLD, meta['fault_tolerance'] - 0.01)
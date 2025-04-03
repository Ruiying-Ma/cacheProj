# Import anything you need below
from collections import defaultdict
import time

# Put tunable constant parameters below
INITIAL_PRIORITY = 1.0
PRIORITY_INCREMENT = 0.1
LATENCY_IMPACT_FACTOR = 0.5
PRIORITY_INVERSION_THRESHOLD = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including a priority score, access frequency, last access timestamp, and affinity group identifier. It also tracks global metrics like average latency and priority inversion occurrences.
cache_metadata = defaultdict(lambda: {
    'priority_score': INITIAL_PRIORITY,
    'access_frequency': 0,
    'last_access_timestamp': 0,
    'affinity_group': None
})

global_metrics = {
    'average_latency': 0.0,
    'priority_inversion_count': 0
}

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata[key]
        adjusted_priority = metadata['priority_score'] - LATENCY_IMPACT_FACTOR * metadata['access_frequency']
        if adjusted_priority < min_priority:
            min_priority = adjusted_priority
            candid_obj_key = key

    # Check for priority inversion
    if min_priority < PRIORITY_INVERSION_THRESHOLD:
        global_metrics['priority_inversion_count'] += 1
        # Escalate priority of affected entries
        for key, metadata in cache_metadata.items():
            if metadata['priority_score'] < PRIORITY_INVERSION_THRESHOLD:
                metadata['priority_score'] += PRIORITY_INCREMENT

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    metadata = cache_metadata[obj.key]
    metadata['priority_score'] += PRIORITY_INCREMENT
    metadata['last_access_timestamp'] = cache_snapshot.access_count
    metadata['access_frequency'] += 1

    # Recalculate average latency
    global_metrics['average_latency'] = (
        (global_metrics['average_latency'] * cache_snapshot.hit_count) + 1
    ) / (cache_snapshot.hit_count + 1)

    # Check for potential priority inversions
    if metadata['priority_score'] < PRIORITY_INVERSION_THRESHOLD:
        global_metrics['priority_inversion_count'] += 1

def update_after_insert(cache_snapshot, obj):
    # Your code below
    metadata = cache_metadata[obj.key]
    metadata['priority_score'] = INITIAL_PRIORITY
    metadata['last_access_timestamp'] = cache_snapshot.access_count
    metadata['access_frequency'] = 1
    metadata['affinity_group'] = obj.key.split('_')[0]  # Example affinity group based on key prefix

    # Update global average latency
    global_metrics['average_latency'] = (
        (global_metrics['average_latency'] * cache_snapshot.miss_count) + 1
    ) / (cache_snapshot.miss_count + 1)

    # Check for immediate priority inversion risks
    if metadata['priority_score'] < PRIORITY_INVERSION_THRESHOLD:
        global_metrics['priority_inversion_count'] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_metadata = cache_metadata[evicted_obj.key]
    affinity_group = evicted_metadata['affinity_group']

    # Adjust priority scores of remaining entries in the same affinity group
    for key, metadata in cache_metadata.items():
        if metadata['affinity_group'] == affinity_group:
            metadata['priority_score'] -= PRIORITY_INCREMENT

    # Update global metrics
    global_metrics['average_latency'] = (
        (global_metrics['average_latency'] * (cache_snapshot.size - evicted_obj.size)) / cache_snapshot.size
    )
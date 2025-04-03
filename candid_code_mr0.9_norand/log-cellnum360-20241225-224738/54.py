# Import anything you need below
from collections import defaultdict
import threading

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQ = 0.5
WEIGHT_LAST_ACCESS = 0.3
WEIGHT_SIZE = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, data size, and a priority score calculated based on a weighted combination of these factors. It also tracks concurrent access patterns to optimize for multi-threaded environments.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'priority_score': {},
    'lock': threading.Lock()
}

def calculate_priority_score(obj, cache_snapshot):
    access_freq = metadata['access_frequency'][obj.key]
    last_access = metadata['last_access_timestamp'].get(obj.key, 0)
    size = obj.size
    current_time = cache_snapshot.access_count

    # Calculate priority score
    score = (WEIGHT_ACCESS_FREQ * access_freq +
             WEIGHT_LAST_ACCESS * (current_time - last_access) +
             WEIGHT_SIZE * size)
    return score

def evict(cache_snapshot, obj):
    candid_obj_key = None
    min_priority_score = float('inf')

    with metadata['lock']:
        for key, cached_obj in cache_snapshot.cache.items():
            score = calculate_priority_score(cached_obj, cache_snapshot)
            if score < min_priority_score:
                min_priority_score = score
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    with metadata['lock']:
        # Update last access timestamp and access frequency
        metadata['last_access_timestamp'][obj.key] = cache_snapshot.access_count
        metadata['access_frequency'][obj.key] += 1

        # Recalculate priority score
        metadata['priority_score'][obj.key] = calculate_priority_score(obj, cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    with metadata['lock']:
        # Initialize metadata for the new object
        metadata['access_frequency'][obj.key] = 1
        metadata['last_access_timestamp'][obj.key] = cache_snapshot.access_count
        metadata['priority_score'][obj.key] = calculate_priority_score(obj, cache_snapshot)

        # Adjust priority scores of existing entries if necessary
        for key in cache_snapshot.cache:
            if key != obj.key:
                metadata['priority_score'][key] = calculate_priority_score(cache_snapshot.cache[key], cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    with metadata['lock']:
        # Remove metadata of the evicted object
        if evicted_obj.key in metadata['access_frequency']:
            del metadata['access_frequency'][evicted_obj.key]
        if evicted_obj.key in metadata['last_access_timestamp']:
            del metadata['last_access_timestamp'][evicted_obj.key]
        if evicted_obj.key in metadata['priority_score']:
            del metadata['priority_score'][evicted_obj.key]

        # Recalibrate priority scores of remaining entries
        for key in cache_snapshot.cache:
            metadata['priority_score'][key] = calculate_priority_score(cache_snapshot.cache[key], cache_snapshot)
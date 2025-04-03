# Import anything you need below
import hashlib

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.3
REDUNDANCY_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency counter for each cache entry, a circular redundancy check value for data integrity, a timestamp for last access, and a dynamic priority score that adapts based on access patterns.
cache_metadata = {
    'frequency': {},  # Maps obj.key to frequency count
    'last_access': {},  # Maps obj.key to last access timestamp
    'redundancy_check': {},  # Maps obj.key to redundancy check value
    'priority_score': {}  # Maps obj.key to dynamic priority score
}

def calculate_redundancy_check(obj):
    # Simple CRC-like function using hashlib
    return int(hashlib.md5(obj.key.encode()).hexdigest(), 16)

def calculate_priority_score(key):
    frequency = cache_metadata['frequency'].get(key, 0)
    last_access = cache_metadata['last_access'].get(key, 0)
    redundancy_check = cache_metadata['redundancy_check'].get(key, 0)
    
    # Calculate priority score based on weighted sum
    priority_score = (
        FREQUENCY_WEIGHT * frequency +
        RECENCY_WEIGHT * last_access +
        REDUNDANCY_WEIGHT * redundancy_check
    )
    return priority_score

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_priority_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = cache_metadata['priority_score'].get(key, float('inf'))
        if score < min_priority_score:
            min_priority_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    key = obj.key
    cache_metadata['frequency'][key] = cache_metadata['frequency'].get(key, 0) + 1
    cache_metadata['last_access'][key] = cache_snapshot.access_count
    cache_metadata['priority_score'][key] = calculate_priority_score(key)

def update_after_insert(cache_snapshot, obj):
    # Your code below
    key = obj.key
    cache_metadata['frequency'][key] = 1
    cache_metadata['last_access'][key] = cache_snapshot.access_count
    cache_metadata['redundancy_check'][key] = calculate_redundancy_check(obj)
    cache_metadata['priority_score'][key] = calculate_priority_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    cache_metadata['frequency'].pop(evicted_key, None)
    cache_metadata['last_access'].pop(evicted_key, None)
    cache_metadata['redundancy_check'].pop(evicted_key, None)
    cache_metadata['priority_score'].pop(evicted_key, None)
    
    # Recalculate priority scores for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['priority_score'][key] = calculate_priority_score(key)
    
    # Verify integrity using redundancy checks
    for key, obj in cache_snapshot.cache.items():
        assert cache_metadata['redundancy_check'][key] == calculate_redundancy_check(obj), "Data integrity check failed"
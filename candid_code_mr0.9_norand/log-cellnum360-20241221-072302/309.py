# Import anything you need below
import math

# Put tunable constant parameters below
DEFAULT_ACCESS_FREQUENCY = 1
DEFAULT_RECENCY = 1
DEFAULT_CONTEXTUAL_PATH_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a vector for each cache entry, representing its access frequency, recency, and contextual path score. It also tracks a dynamic entropy value for the entire cache to measure unpredictability in access patterns.
cache_metadata = {
    'vectors': {},  # {obj.key: {'frequency': int, 'recency': int, 'contextual_path_score': int}}
    'dynamic_entropy': 0.0
}

def calculate_entropy(cache_snapshot):
    # Calculate entropy based on access patterns
    total_accesses = cache_snapshot.access_count
    if total_accesses == 0:
        return 0.0
    hit_ratio = cache_snapshot.hit_count / total_accesses
    miss_ratio = cache_snapshot.miss_count / total_accesses
    entropy = 0.0
    if hit_ratio > 0:
        entropy -= hit_ratio * math.log(hit_ratio)
    if miss_ratio > 0:
        entropy -= miss_ratio * math.log(miss_ratio)
    return entropy

def calculate_composite_score(vector, entropy):
    # Calculate composite score using vector arithmetic logic
    return (vector['frequency'] + vector['recency'] + vector['contextual_path_score']) / (1 + entropy)

def evict(cache_snapshot, obj):
    candid_obj_key = None
    min_score = float('inf')
    
    # Calculate the composite score for each entry and find the one with the lowest score
    for key, cached_obj in cache_snapshot.cache.items():
        vector = cache_metadata['vectors'].get(key, {})
        score = calculate_composite_score(vector, cache_metadata['dynamic_entropy'])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Update the vector for the accessed entry
    vector = cache_metadata['vectors'].setdefault(obj.key, {
        'frequency': DEFAULT_ACCESS_FREQUENCY,
        'recency': DEFAULT_RECENCY,
        'contextual_path_score': DEFAULT_CONTEXTUAL_PATH_SCORE
    })
    vector['frequency'] += 1
    vector['recency'] += 1
    vector['contextual_path_score'] += 1  # Simplified update logic
    
    # Recalculate dynamic entropy
    cache_metadata['dynamic_entropy'] = calculate_entropy(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    # Initialize the vector for the new object
    cache_metadata['vectors'][obj.key] = {
        'frequency': DEFAULT_ACCESS_FREQUENCY,
        'recency': DEFAULT_RECENCY,
        'contextual_path_score': DEFAULT_CONTEXTUAL_PATH_SCORE
    }
    
    # Update dynamic entropy
    cache_metadata['dynamic_entropy'] = calculate_entropy(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Remove the vector for the evicted object
    if evicted_obj.key in cache_metadata['vectors']:
        del cache_metadata['vectors'][evicted_obj.key]
    
    # Recalculate dynamic entropy
    cache_metadata['dynamic_entropy'] = calculate_entropy(cache_snapshot)
    
    # Adjust vectors of remaining entries (simplified logic)
    for vector in cache_metadata['vectors'].values():
        vector['frequency'] = max(1, vector['frequency'] - 1)
        vector['recency'] = max(1, vector['recency'] - 1)
        vector['contextual_path_score'] = max(1, vector['contextual_path_score'] - 1)
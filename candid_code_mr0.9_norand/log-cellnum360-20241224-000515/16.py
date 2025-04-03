# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQ = 0.3
WEIGHT_RECENCY = 0.3
WEIGHT_IMPORTANCE = 0.3
WEIGHT_DECAY = 0.1
DEFAULT_DECAY_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, data importance score, and a decay factor for each cache entry. The data importance score is calculated based on the type of data and its historical access patterns.
metadata = defaultdict(lambda: {
    'access_freq': 0,
    'recency': 0,
    'importance': 0,
    'decay_factor': DEFAULT_DECAY_FACTOR
})

def calculate_importance(obj):
    # Placeholder for a real importance calculation based on object characteristics
    return 1.0

def calculate_composite_score(key, cache_snapshot):
    data = metadata[key]
    access_freq = data['access_freq']
    recency = data['recency']
    importance = data['importance']
    decay_factor = data['decay_factor']
    
    # Calculate the composite score
    composite_score = (
        WEIGHT_ACCESS_FREQ * (1 / (access_freq + 1)) +
        WEIGHT_RECENCY * recency +
        WEIGHT_IMPORTANCE * importance +
        WEIGHT_DECAY * decay_factor
    )
    return composite_score

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key, cache_snapshot)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata[key]['access_freq'] += 1
    metadata[key]['recency'] = cache_snapshot.access_count
    # Recalculate importance if necessary
    metadata[key]['importance'] = calculate_importance(obj)
    # Adjust decay factor
    metadata[key]['decay_factor'] *= 0.99  # Slightly reduce the weight of older accesses

def update_after_insert(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata[key]['access_freq'] = 1
    metadata[key]['recency'] = cache_snapshot.access_count
    metadata[key]['importance'] = calculate_importance(obj)
    metadata[key]['decay_factor'] = DEFAULT_DECAY_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    for key in cache_snapshot.cache:
        # Recalibrate decay factor for remaining entries
        metadata[key]['decay_factor'] *= 0.99  # Example adjustment
    # Optionally adjust weights (not implemented here, but could be based on access patterns)
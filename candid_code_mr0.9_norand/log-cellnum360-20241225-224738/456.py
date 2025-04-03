# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
HEURISTIC_WEIGHT = 0.5
RESOURCE_WEIGHT = 0.3
CONTEXT_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, resource usage profile, and contextual tags for each cache entry. It also keeps a dynamic heuristic score that predicts future access patterns based on historical data and current system context.
metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'resource_usage': {},
    'contextual_tags': {},
    'heuristic_score': {}
}

def calculate_composite_score(key):
    freq = metadata['access_frequency'][key]
    recency = metadata['recency'][key]
    resource = metadata['resource_usage'][key]
    context = metadata['contextual_tags'][key]
    heuristic = metadata['heuristic_score'][key]
    
    # Composite score calculation
    composite_score = (HEURISTIC_WEIGHT * heuristic +
                       RESOURCE_WEIGHT * resource +
                       CONTEXT_WEIGHT * context)
    return composite_score

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    
    # Adjust heuristic score based on current context
    metadata['heuristic_score'][key] = (metadata['access_frequency'][key] + 
                                        metadata['recency'][key] / cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['resource_usage'][key] = obj.size
    metadata['contextual_tags'][key] = 1  # Default context tag
    metadata['heuristic_score'][key] = (metadata['access_frequency'][key] + 
                                        metadata['recency'][key] / cache_snapshot.access_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['recency'][evicted_key]
    del metadata['resource_usage'][evicted_key]
    del metadata['contextual_tags'][evicted_key]
    del metadata['heuristic_score'][evicted_key]
    
    # Recalibrate heuristic model if needed (not implemented in detail here)
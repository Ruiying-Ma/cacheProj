# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.3
PREDICTED_LOAD_WEIGHT = 0.2
CAPACITY_ALLOCATION_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, predicted future load, and dynamic capacity allocation for each cache entry. It also tracks a heuristic score for each entry, which is a weighted combination of these factors.
metadata = defaultdict(lambda: {
    'frequency': 0,
    'recency': 0,
    'predicted_load': 0,
    'capacity_allocation': 0,
    'heuristic_score': 0
})

def calculate_heuristic_score(obj_key):
    data = metadata[obj_key]
    return (FREQUENCY_WEIGHT * data['frequency'] +
            RECENCY_WEIGHT * data['recency'] +
            PREDICTED_LOAD_WEIGHT * data['predicted_load'] +
            CAPACITY_ALLOCATION_WEIGHT * data['capacity_allocation'])

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_heuristic_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    obj_key = obj.key
    metadata[obj_key]['frequency'] += 1
    metadata[obj_key]['recency'] = cache_snapshot.access_count
    metadata[obj_key]['heuristic_score'] = calculate_heuristic_score(obj_key)

def update_after_insert(cache_snapshot, obj):
    # Your code below
    obj_key = obj.key
    metadata[obj_key]['frequency'] = 1
    metadata[obj_key]['recency'] = cache_snapshot.access_count
    metadata[obj_key]['predicted_load'] = 1  # Initial prediction
    metadata[obj_key]['capacity_allocation'] = obj.size / cache_snapshot.capacity
    metadata[obj_key]['heuristic_score'] = calculate_heuristic_score(obj_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_key = evicted_obj.key
    del metadata[evicted_key]
    
    for key in cache_snapshot.cache:
        metadata[key]['capacity_allocation'] = cache_snapshot.cache[key].size / cache_snapshot.capacity
        metadata[key]['predicted_load'] = max(0, metadata[key]['predicted_load'] - 1)  # Decrease predicted load
        metadata[key]['heuristic_score'] = calculate_heuristic_score(key)
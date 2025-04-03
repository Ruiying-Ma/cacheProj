# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
TEMPORAL_DECAY_FACTOR = 0.9
INITIAL_PREDICTED_USAGE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of cache levels, each with its own temporal decay factor. It tracks access frequency, recency, and predicted future usage for each cache entry. Additionally, it maintains a proactive eviction score based on these factors.
cache_metadata = {
    'access_frequency': defaultdict(int),
    'recency_timestamp': {},
    'predicted_future_usage': defaultdict(lambda: INITIAL_PREDICTED_USAGE),
    'eviction_score': {}
}

def calculate_eviction_score(key, cache_snapshot):
    frequency = cache_metadata['access_frequency'][key]
    recency = cache_metadata['recency_timestamp'][key]
    predicted_usage = cache_metadata['predicted_future_usage'][key]
    current_time = cache_snapshot.access_count

    # Composite score calculation
    score = (TEMPORAL_DECAY_FACTOR * (current_time - recency) +
             frequency +
             predicted_usage)
    return score

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_eviction_score(key, cache_snapshot)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    key = obj.key
    cache_metadata['access_frequency'][key] += 1
    cache_metadata['recency_timestamp'][key] = cache_snapshot.access_count

    # Recalculate predicted future usage
    cache_metadata['predicted_future_usage'][key] *= 1.1  # Example adjustment
    # Update eviction score
    cache_metadata['eviction_score'][key] = calculate_eviction_score(key, cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    # Your code below
    key = obj.key
    cache_metadata['access_frequency'][key] = 1
    cache_metadata['recency_timestamp'][key] = cache_snapshot.access_count
    cache_metadata['predicted_future_usage'][key] = INITIAL_PREDICTED_USAGE

    # Calculate initial eviction score
    cache_metadata['eviction_score'][key] = calculate_eviction_score(key, cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del cache_metadata['access_frequency'][evicted_key]
    del cache_metadata['recency_timestamp'][evicted_key]
    del cache_metadata['predicted_future_usage'][evicted_key]
    del cache_metadata['eviction_score'][evicted_key]

    # Recalibrate temporal decay factors for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['predicted_future_usage'][key] *= TEMPORAL_DECAY_FACTOR
        # Update eviction score
        cache_metadata['eviction_score'][key] = calculate_eviction_score(key, cache_snapshot)
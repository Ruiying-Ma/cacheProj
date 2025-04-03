# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ACCESS_PROBABILITY = 0.5
DEFAULT_SCALING_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a history buffer to track recent access patterns, predictive analytics to forecast future access probabilities, dynamic scaling factors to adjust cache priorities based on access latency, and a timestamp for each cache entry to monitor recency.
history_buffer = defaultdict(lambda: {'access_count': 0, 'last_access_time': 0, 'access_probability': DEFAULT_ACCESS_PROBABILITY, 'scaling_factor': DEFAULT_SCALING_FACTOR})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a score for each cache entry based on predicted future access probability, access latency, and recency. The entry with the lowest score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = history_buffer[key]
        recency = cache_snapshot.access_count - metadata['last_access_time']
        score = (metadata['access_probability'] * metadata['scaling_factor']) / (recency + 1)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the history buffer with the latest access information, recalculates the predictive analytics for future access probability, adjusts the dynamic scaling factor based on the observed access latency, and refreshes the timestamp for the accessed entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata = history_buffer[obj.key]
    metadata['access_count'] += 1
    metadata['last_access_time'] = cache_snapshot.access_count
    metadata['access_probability'] = metadata['access_count'] / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    # Adjust scaling factor based on some observed latency metric (not provided, so using a placeholder)
    metadata['scaling_factor'] = DEFAULT_SCALING_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its entry in the history buffer, sets an initial predictive access probability, assigns a default dynamic scaling factor based on average access latency, and records the current timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    history_buffer[obj.key] = {
        'access_count': 0,
        'last_access_time': cache_snapshot.access_count,
        'access_probability': DEFAULT_ACCESS_PROBABILITY,
        'scaling_factor': DEFAULT_SCALING_FACTOR
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted entry from the history buffer, recalibrates the predictive analytics model to account for the change in cache composition, and adjusts the dynamic scaling factors for remaining entries if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in history_buffer:
        del history_buffer[evicted_obj.key]
    
    # Recalibrate predictive analytics model (not specified, so using a placeholder)
    # Adjust scaling factors for remaining entries if necessary (not specified, so using a placeholder)
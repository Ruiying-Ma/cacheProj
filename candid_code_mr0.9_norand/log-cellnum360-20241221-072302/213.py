# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_INVERSE_ACCESS_FREQ = 0.4
WEIGHT_TEMPORAL_VARIANCE = 0.3
WEIGHT_RESOURCE_ALLOCATION_SCORE = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, synchronization status, and resource allocation pattern score for each cache entry.
metadata = defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_timestamp': 0,
    'temporal_variance': 0,
    'resource_allocation_score': 1.0,
    'synchronization_status': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of inverse access frequency, temporal variance of access, and resource allocation pattern score, prioritizing entries with lower synchronization status.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        inverse_access_freq = 1 / (meta['access_frequency'] + 1)
        temporal_variance = meta['temporal_variance']
        resource_allocation_score = meta['resource_allocation_score']
        
        composite_score = (
            WEIGHT_INVERSE_ACCESS_FREQ * inverse_access_freq +
            WEIGHT_TEMPORAL_VARIANCE * temporal_variance +
            WEIGHT_RESOURCE_ALLOCATION_SCORE * resource_allocation_score
        )
        
        # Prioritize lower synchronization status
        if meta['synchronization_status'] < min_score or (
            meta['synchronization_status'] == min_score and composite_score < min_score):
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the last access timestamp, recalculates the temporal variance, and adjusts the resource allocation pattern score based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    current_time = cache_snapshot.access_count
    last_access_time = meta['last_access_timestamp']
    meta['temporal_variance'] = (meta['temporal_variance'] + (current_time - last_access_time) ** 2) / 2
    meta['last_access_timestamp'] = current_time
    # Adjust resource allocation pattern score based on some heuristic
    meta['resource_allocation_score'] *= 0.9

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to one, sets the last access timestamp to the current time, estimates initial temporal variance, and assigns a default resource allocation pattern score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'temporal_variance': 0,
        'resource_allocation_score': 1.0,
        'synchronization_status': 0
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the resource allocation pattern scores of remaining entries to reflect the change in cache composition and updates synchronization status to ensure consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    for key in cache_snapshot.cache:
        metadata[key]['resource_allocation_score'] *= 1.1
        metadata[key]['synchronization_status'] += 1
# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_AGE = 1.0
WEIGHT_CONTENTION_LEVEL = 1.0
WEIGHT_PREDICTIVE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, contention level, and a predictive score for each cache entry. It also tracks a global contention index and a temporal redundancy factor for the cache.
metadata = defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_timestamp': 0,
    'contention_level': 0,
    'predictive_score': 0
})

global_contention_index = 0
temporal_redundancy_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of its access frequency, age (time since last access), contention level, and predictive score. The entry with the lowest composite score is selected for eviction.
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
        age = cache_snapshot.access_count - meta['last_access_timestamp']
        composite_score = (
            WEIGHT_ACCESS_FREQUENCY * meta['access_frequency'] +
            WEIGHT_AGE * age +
            WEIGHT_CONTENTION_LEVEL * meta['contention_level'] +
            WEIGHT_PREDICTIVE_SCORE * meta['predictive_score']
        )
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency of the entry is incremented, the last access timestamp is updated to the current time, and the predictive score is adjusted based on the current contention level and temporal redundancy factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    meta['predictive_score'] = (meta['contention_level'] + temporal_redundancy_factor) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to one, sets the last access timestamp to the current time, and calculates an initial predictive score based on the global contention index and temporal redundancy factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'contention_level': global_contention_index,
        'predictive_score': (global_contention_index + temporal_redundancy_factor) / 2
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the global contention index is updated based on the current cache load and access patterns, and the temporal redundancy factor is recalibrated to reflect the recent eviction's impact on cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global global_contention_index, temporal_redundancy_factor
    
    cache_load = cache_snapshot.size / cache_snapshot.capacity
    global_contention_index = cache_load * cache_snapshot.access_count
    temporal_redundancy_factor = (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count + 1))
# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.3
PRIORITY_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, priority score, and a dynamic allocation weight that adjusts based on system load and access patterns.
metadata = defaultdict(lambda: {
    'frequency': 0,
    'last_access': 0,
    'priority': 0,
    'dynamic_weight': 1.0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each entry, which is a weighted sum of inverse frequency, recency, and priority. The entry with the lowest score is chosen for eviction, with dynamic allocation weights adjusting the influence of each factor based on current load conditions.
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
        frequency_score = 1 / (meta['frequency'] + 1)
        recency_score = cache_snapshot.access_count - meta['last_access']
        priority_score = 1 / (meta['priority'] + 1)
        
        composite_score = (
            FREQUENCY_WEIGHT * frequency_score +
            RECENCY_WEIGHT * recency_score +
            PRIORITY_WEIGHT * priority_score
        ) * meta['dynamic_weight']
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the priority score is recalculated to reflect increased importance. The dynamic allocation weight is adjusted slightly to favor frequently accessed entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['frequency'] += 1
    meta['last_access'] = cache_snapshot.access_count
    meta['priority'] += 1
    meta['dynamic_weight'] *= 1.05  # Slightly favor frequently accessed entries

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency to one, sets the last access timestamp to the current time, assigns a default priority score, and calculates an initial dynamic allocation weight based on current system load and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'frequency': 1,
        'last_access': cache_snapshot.access_count,
        'priority': 1,
        'dynamic_weight': 1.0  # Initial weight
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy reassesses the dynamic allocation weights for remaining entries to optimize load distribution, potentially increasing the weight for entries with similar characteristics to the evicted one if they are underrepresented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_meta = metadata[evicted_obj.key]
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        if meta['priority'] == evicted_meta['priority']:
            meta['dynamic_weight'] *= 1.1  # Increase weight for similar entries
    del metadata[evicted_obj.key]
# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIME = 1.0
WEIGHT_DATA_SIZE = 1.0
WEIGHT_COHERENCE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data size, and a coherence score for each cache entry. It also tracks overall cache load and bandwidth usage.
metadata = {}
overall_cache_load = 0
bandwidth_usage = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access time, large data size, and low coherence score. It also considers current cache load and bandwidth usage to ensure load balancing.
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
        score = (WEIGHT_ACCESS_FREQUENCY * meta['access_frequency'] +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - meta['last_access_time']) +
                 WEIGHT_DATA_SIZE * cached_obj.size +
                 WEIGHT_COHERENCE_SCORE * meta['coherence_score'])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the last access time to the current time, and recalculates the coherence score based on recent access patterns. It also updates the overall cache load and bandwidth usage statistics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    meta['access_frequency'] += 1
    meta['last_access_time'] = cache_snapshot.access_count
    meta['coherence_score'] = calculate_coherence_score(meta)
    update_overall_cache_load_and_bandwidth(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the last access time to the current time, assigns an initial coherence score, and updates the overall cache load and bandwidth usage statistics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'coherence_score': initial_coherence_score(),
        'size': obj.size
    }
    update_overall_cache_load_and_bandwidth(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the metadata of the evicted entry, recalculates the overall cache load, and adjusts the bandwidth usage statistics to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata:
        del metadata[key]
    update_overall_cache_load_and_bandwidth(cache_snapshot)

def calculate_coherence_score(meta):
    # Placeholder for coherence score calculation logic
    return meta['access_frequency'] / (time.time() - meta['last_access_time'] + 1)

def initial_coherence_score():
    # Placeholder for initial coherence score
    return 1.0

def update_overall_cache_load_and_bandwidth(cache_snapshot):
    global overall_cache_load, bandwidth_usage
    overall_cache_load = cache_snapshot.size
    bandwidth_usage = sum(obj.size for obj in cache_snapshot.cache.values())
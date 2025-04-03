# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIME = 1.0
WEIGHT_PREDICTIVE_ACCESS = 1.0
WEIGHT_MEMORY_BANDWIDTH = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data synchronization status, and predictive access patterns. It also tracks memory bandwidth usage and load distribution across cache lines.
access_frequency = collections.defaultdict(int)
last_access_time = collections.defaultdict(int)
predictive_access_pattern = collections.defaultdict(float)
memory_bandwidth_usage = collections.defaultdict(int)
load_distribution = collections.defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access time, low predictive access likelihood, and high memory bandwidth usage. It also considers load distribution to avoid overloading specific cache lines.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency[key] +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time[key]) +
                 WEIGHT_PREDICTIVE_ACCESS * predictive_access_pattern[key] +
                 WEIGHT_MEMORY_BANDWIDTH * memory_bandwidth_usage[key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, adjusts the predictive access pattern based on recent access trends, and recalculates memory bandwidth usage for the accessed cache line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    predictive_access_pattern[key] = 0.5 * predictive_access_pattern[key] + 0.5 * access_frequency[key]
    memory_bandwidth_usage[key] += obj.size

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, establishes an initial predictive access pattern based on historical data, and updates memory bandwidth usage and load distribution to reflect the new insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    predictive_access_pattern[key] = 1.0
    memory_bandwidth_usage[key] = obj.size
    load_distribution[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the metadata associated with the evicted object, recalculates the load distribution to ensure balanced cache usage, and adjusts memory bandwidth usage to account for the freed space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del access_frequency[evicted_key]
    del last_access_time[evicted_key]
    del predictive_access_pattern[evicted_key]
    del memory_bandwidth_usage[evicted_key]
    del load_distribution[evicted_key]
    
    # Recalculate load distribution
    total_load = sum(load_distribution.values())
    for key in load_distribution:
        load_distribution[key] = load_distribution[key] / total_load
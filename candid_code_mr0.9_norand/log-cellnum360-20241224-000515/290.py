# Import anything you need below
import math

# Put tunable constant parameters below
INITIAL_PRIORITY_WEIGHT = 1.0
RESOURCE_ALLOCATION_SCORE_FACTOR = 0.5
GLOBAL_RESOURCE_AVAILABILITY_INDEX_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, priority weight, and resource allocation score for each cache entry. It also tracks a global resource availability index to dynamically adjust priorities.
metadata = {}
global_resource_availability_index = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by performing a comprehensive analysis of all cache entries, considering the lowest priority weight adjusted by the resource allocation score and access frequency. Entries with the least recent access time are considered when weights are equal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    min_last_access_time = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        entry = metadata[key]
        adjusted_priority = entry['priority_weight'] - (entry['resource_allocation_score'] * RESOURCE_ALLOCATION_SCORE_FACTOR) + (entry['access_frequency'] * GLOBAL_RESOURCE_AVAILABILITY_INDEX_FACTOR)
        
        if adjusted_priority < min_priority or (adjusted_priority == min_priority and entry['last_access_time'] < min_last_access_time):
            min_priority = adjusted_priority
            min_last_access_time = entry['last_access_time']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and updates the last access time of the entry. It also recalculates the priority weight based on the current resource allocation score and global resource availability index.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    entry = metadata[obj.key]
    entry['access_frequency'] += 1
    entry['last_access_time'] = cache_snapshot.access_count
    entry['priority_weight'] = INITIAL_PRIORITY_WEIGHT + (entry['resource_allocation_score'] * global_resource_availability_index)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and sets the last access time to the current time. It assigns an initial priority weight based on the object's importance and adjusts it according to the resource allocation score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'priority_weight': INITIAL_PRIORITY_WEIGHT,
        'resource_allocation_score': obj.size / cache_snapshot.capacity
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the global resource availability index to reflect the freed resources. It recalibrates the priority weights of remaining entries to ensure optimal scheduling and resource allocation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global global_resource_availability_index
    global_resource_availability_index += evicted_obj.size / cache_snapshot.capacity

    for key, entry in metadata.items():
        entry['priority_weight'] = INITIAL_PRIORITY_WEIGHT + (entry['resource_allocation_score'] * global_resource_availability_index)
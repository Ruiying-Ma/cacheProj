# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1
PRIORITY_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, a virtual allocation map to track resource distribution, and a load optimization index to balance cache load.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
virtual_allocation_map = defaultdict(int)
load_optimization_index = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on the lowest dynamic priority score, considering both the virtual allocation map and load optimization index to ensure minimal impact on system performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_scores[key] + virtual_allocation_map[key] - load_optimization_index
        if priority < min_priority:
            min_priority = priority
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the dynamic priority score of the accessed entry is increased, the virtual allocation map is adjusted to reflect the increased importance, and the load optimization index is recalibrated to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] += PRIORITY_INCREMENT
    virtual_allocation_map[obj.key] += 1
    load_optimization_index = sum(virtual_allocation_map.values()) / len(cache_snapshot.cache)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial dynamic priority score based on predicted access patterns, updates the virtual allocation map to include the new entry, and recalibrates the load optimization index to accommodate the change.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] = INITIAL_PRIORITY_SCORE
    virtual_allocation_map[obj.key] = 1
    load_optimization_index = sum(virtual_allocation_map.values()) / len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the entry from the virtual allocation map, redistributes resources to remaining entries, and adjusts the load optimization index to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in priority_scores:
        del priority_scores[evicted_obj.key]
    if evicted_obj.key in virtual_allocation_map:
        del virtual_allocation_map[evicted_obj.key]
    
    # Redistribute resources
    total_allocation = sum(virtual_allocation_map.values())
    if total_allocation > 0:
        for key in virtual_allocation_map:
            virtual_allocation_map[key] = virtual_allocation_map[key] / total_allocation
    
    load_optimization_index = sum(virtual_allocation_map.values()) / len(cache_snapshot.cache)
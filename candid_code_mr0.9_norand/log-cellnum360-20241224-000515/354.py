# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
SYNC_LEVEL_INCREMENT = 1
INITIAL_SYNC_LEVEL = 1
INITIAL_TEMPORAL_PATTERN = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of cache blocks, each with a synchronization level indicating its access frequency and recency. It also tracks temporal access patterns and a quantum flux value representing the dynamic load distribution across cache levels.
sync_levels = defaultdict(lambda: INITIAL_SYNC_LEVEL)
temporal_patterns = defaultdict(lambda: INITIAL_TEMPORAL_PATTERN)
quantum_flux = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by identifying the cache block with the lowest synchronization level and least recent access pattern. It also considers the quantum flux distribution to ensure balanced load across cache levels, evicting from the level with the highest flux.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_sync_level = float('inf')
    min_temporal_pattern = float('inf')
    
    # Find the cache block with the lowest sync level and least recent access pattern
    for key, cached_obj in cache_snapshot.cache.items():
        if (sync_levels[key] < min_sync_level or
            (sync_levels[key] == min_sync_level and temporal_patterns[key] < min_temporal_pattern)):
            min_sync_level = sync_levels[key]
            min_temporal_pattern = temporal_patterns[key]
            candid_obj_key = key
    
    # Consider quantum flux distribution
    if candid_obj_key:
        max_flux_level = max(quantum_flux.values())
        if quantum_flux[candid_obj_key] < max_flux_level:
            for key in cache_snapshot.cache:
                if quantum_flux[key] == max_flux_level:
                    candid_obj_key = key
                    break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the synchronization level of the accessed block is incremented, and its temporal pattern is updated to reflect the current access time. The quantum flux value is adjusted to redistribute load based on the updated access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    sync_levels[key] += SYNC_LEVEL_INCREMENT
    temporal_patterns[key] = cache_snapshot.access_count
    quantum_flux[key] = sync_levels[key] / (cache_snapshot.access_count + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its synchronization level and temporal pattern based on predicted access frequency. The quantum flux is recalibrated to accommodate the new object, ensuring even load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    sync_levels[key] = INITIAL_SYNC_LEVEL
    temporal_patterns[key] = cache_snapshot.access_count
    quantum_flux[key] = sync_levels[key] / (cache_snapshot.access_count + 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the synchronization levels of remaining blocks are recalibrated to reflect the new cache state. The temporal patterns are adjusted to account for the removed block, and the quantum flux is redistributed to maintain balanced load across cache levels.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in sync_levels:
        del sync_levels[evicted_key]
    if evicted_key in temporal_patterns:
        del temporal_patterns[evicted_key]
    if evicted_key in quantum_flux:
        del quantum_flux[evicted_key]
    
    # Recalibrate synchronization levels and quantum flux
    for key in cache_snapshot.cache:
        quantum_flux[key] = sync_levels[key] / (cache_snapshot.access_count + 1)
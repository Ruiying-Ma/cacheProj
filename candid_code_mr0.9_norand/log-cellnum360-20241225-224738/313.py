# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALIGNMENT_INCREMENT = 1
PREDICTIVE_AUGMENTATION_DECAY = 0.9
LOAD_EQUILIBRIUM_ADJUSTMENT = 0.1
MEMORY_EXPANSION_FACTOR_BASE = 1.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a systematic alignment score for each cache entry, a memory expansion factor indicating potential growth of data, a predictive augmentation score based on access patterns, and a load equilibrium index to balance cache load.
systematic_alignment = defaultdict(int)
predictive_augmentation = defaultdict(float)
load_equilibrium_index = defaultdict(float)
memory_expansion_factor = MEMORY_EXPANSION_FACTOR_BASE

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of systematic alignment and predictive augmentation, while ensuring the load equilibrium index remains balanced across cache entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = systematic_alignment[key] + predictive_augmentation[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the systematic alignment score is incremented to reflect increased alignment, the predictive augmentation score is updated based on recent access patterns, and the load equilibrium index is adjusted to reflect the current load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    systematic_alignment[key] += ALIGNMENT_INCREMENT
    predictive_augmentation[key] = predictive_augmentation[key] * PREDICTIVE_AUGMENTATION_DECAY + 1
    load_equilibrium_index[key] += LOAD_EQUILIBRIUM_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the memory expansion factor is recalculated to account for potential growth, the systematic alignment score is initialized, and the load equilibrium index is updated to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    systematic_alignment[key] = 0
    predictive_augmentation[key] = 0
    load_equilibrium_index[key] = 1 / len(cache_snapshot.cache)
    global memory_expansion_factor
    memory_expansion_factor = MEMORY_EXPANSION_FACTOR_BASE * (cache_snapshot.size / cache_snapshot.capacity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the memory expansion factor is adjusted to reflect the reduced cache size, the load equilibrium index is recalibrated to ensure even distribution, and the predictive augmentation scores of remaining entries are slightly adjusted to reflect the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    del systematic_alignment[key]
    del predictive_augmentation[key]
    del load_equilibrium_index[key]
    
    global memory_expansion_factor
    memory_expansion_factor = MEMORY_EXPANSION_FACTOR_BASE * (cache_snapshot.size / cache_snapshot.capacity)
    
    for key in cache_snapshot.cache:
        predictive_augmentation[key] *= PREDICTIVE_AUGMENTATION_DECAY
        load_equilibrium_index[key] = 1 / len(cache_snapshot.cache)
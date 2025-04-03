# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_BATCH_FREQUENCY = 1
INITIAL_PRIORITY_INDEX = 1.0
OPTIMIZATION_FACTOR_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a sequential access pattern score, a batch access frequency counter, and a refined algorithmic priority index for each cache entry. It also tracks a global system optimization factor that adjusts based on overall cache performance.
metadata = {
    'sequential_access_score': defaultdict(int),
    'batch_frequency_counter': defaultdict(lambda: INITIAL_BATCH_FREQUENCY),
    'algorithmic_priority_index': defaultdict(lambda: INITIAL_PRIORITY_INDEX),
    'system_optimization_factor': 1.0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of sequential access pattern, batch frequency, and algorithmic priority, adjusted by the system optimization factor to ensure balanced performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            metadata['sequential_access_score'][key] +
            metadata['batch_frequency_counter'][key] +
            metadata['algorithmic_priority_index'][key]
        ) * metadata['system_optimization_factor']
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequential access pattern score is incremented, the batch frequency counter is updated to reflect recent access, and the algorithmic priority index is refined based on the current system optimization factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['sequential_access_score'][key] += 1
    metadata['batch_frequency_counter'][key] += 1
    metadata['algorithmic_priority_index'][key] *= metadata['system_optimization_factor']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequential access pattern score is initialized, the batch frequency counter is set to a baseline value, and the algorithmic priority index is calculated using initial system optimization parameters.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['sequential_access_score'][key] = 0
    metadata['batch_frequency_counter'][key] = INITIAL_BATCH_FREQUENCY
    metadata['algorithmic_priority_index'][key] = INITIAL_PRIORITY_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the system optimization factor is recalibrated based on the performance impact of the eviction, and the remaining entries' metadata are adjusted to reflect the new optimization context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate the system optimization factor
    if cache_snapshot.hit_count > 0:
        hit_ratio = cache_snapshot.hit_count / cache_snapshot.access_count
        metadata['system_optimization_factor'] += OPTIMIZATION_FACTOR_ADJUSTMENT * (hit_ratio - 0.5)
    
    # Adjust remaining entries' metadata
    for key in cache_snapshot.cache:
        metadata['algorithmic_priority_index'][key] *= metadata['system_optimization_factor']
# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_STRATIFICATION_INDEX = 1
DEFAULT_COHERENCE_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a stratification index for data categorization, a coherence score for structural integrity, an operational redundancy count, and a synchronization index to track access patterns.
stratification_index = defaultdict(lambda: DEFAULT_STRATIFICATION_INDEX)
coherence_score = defaultdict(lambda: DEFAULT_COHERENCE_SCORE)
operational_redundancy = defaultdict(int)
synchronization_index = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest stratification index, indicating less critical data, and the highest operational redundancy, suggesting it can be reconstructed or fetched again with minimal cost.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_stratification = float('inf')
    max_redundancy = -1
    
    for key, cached_obj in cache_snapshot.cache.items():
        if (stratification_index[key] < min_stratification) or \
           (stratification_index[key] == min_stratification and operational_redundancy[key] > max_redundancy):
            min_stratification = stratification_index[key]
            max_redundancy = operational_redundancy[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the stratification index of the accessed data is increased to reflect its importance, the coherence score is recalculated to ensure structural integrity, and the synchronization index is updated to reflect the latest access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    stratification_index[obj.key] += 1
    coherence_score[obj.key] = calculate_coherence(cache_snapshot, obj)
    synchronization_index[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the stratification index is initialized based on the data's initial importance, the coherence score is set to a default value, operational redundancy is assessed, and the synchronization index is updated to include the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    stratification_index[obj.key] = DEFAULT_STRATIFICATION_INDEX
    coherence_score[obj.key] = DEFAULT_COHERENCE_SCORE
    operational_redundancy[obj.key] = assess_redundancy(obj)
    synchronization_index[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the stratification index of remaining entries is adjusted to reflect the new data landscape, coherence scores are recalibrated to maintain structural integrity, and the synchronization index is updated to remove the evicted entry's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del stratification_index[evicted_obj.key]
    del coherence_score[evicted_obj.key]
    del operational_redundancy[evicted_obj.key]
    del synchronization_index[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        coherence_score[key] = calculate_coherence(cache_snapshot, cache_snapshot.cache[key])

def calculate_coherence(cache_snapshot, obj):
    # Placeholder function to calculate coherence score
    return DEFAULT_COHERENCE_SCORE

def assess_redundancy(obj):
    # Placeholder function to assess operational redundancy
    return 0
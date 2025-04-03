# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1.0
ACCESS_FREQUENCY_WEIGHT = 0.5
PREDICTED_ACCESS_WEIGHT = 0.3
RESOURCE_ALLOCATION_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, a predictive index for future access patterns, and a resource allocation map for parallel processing capabilities.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
access_frequencies = defaultdict(int)
predicted_accesses = defaultdict(int)
resource_allocation_map = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest dynamic priority score, which is calculated based on recent access frequency, predicted future access, and current resource allocation efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (ACCESS_FREQUENCY_WEIGHT * access_frequencies[key] +
                 PREDICTED_ACCESS_WEIGHT * predicted_accesses[key] +
                 RESOURCE_ALLOCATION_WEIGHT * resource_allocation_map[key])
        
        if score < min_priority_score:
            min_priority_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the dynamic priority score of the accessed entry is increased, the predictive index is updated to reflect the new access pattern, and the resource allocation map is adjusted to optimize parallel processing for similar future requests.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] += 1
    priority_scores[key] += 1
    predicted_accesses[key] += 1
    resource_allocation_map[key] += 0.1  # Example adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its dynamic priority score based on initial access predictions, updates the predictive index to include the new entry, and adjusts the resource allocation map to accommodate the new entry's processing needs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    priority_scores[key] = INITIAL_PRIORITY_SCORE
    access_frequencies[key] = 1
    predicted_accesses[key] = 1
    resource_allocation_map[key] = 0.5  # Example initial allocation

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic priority scores of remaining entries, refines the predictive index to improve future access predictions, and reallocates resources in the map to enhance parallel processing efficiency for the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]
        del access_frequencies[evicted_key]
        del predicted_accesses[evicted_key]
        del resource_allocation_map[evicted_key]
    
    for key in cache_snapshot.cache:
        priority_scores[key] *= 0.9  # Example recalibration
        predicted_accesses[key] *= 0.9
        resource_allocation_map[key] *= 0.9
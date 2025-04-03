# Import anything you need below
import math
from collections import defaultdict, deque

# Put tunable constant parameters below
DEFAULT_ENTROPY_SCORE = 1000
TEMPORAL_VECTOR_SIZE = 10
SYNC_INDEX_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal vector for each cache entry, representing the access pattern over time, and an entropy score that quantifies the predictability of future accesses. It also includes a synchronization index that aligns with system-wide access trends.
temporal_vectors = defaultdict(lambda: deque([0] * TEMPORAL_VECTOR_SIZE, maxlen=TEMPORAL_VECTOR_SIZE))
entropy_scores = defaultdict(lambda: DEFAULT_ENTROPY_SCORE)
sync_indices = defaultdict(float)

def calculate_entropy(temporal_vector):
    total = sum(temporal_vector)
    if total == 0:
        return 0
    probabilities = [x / total for x in temporal_vector]
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return entropy

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the highest entropy score, indicating the least predictable access pattern, and the lowest synchronization index, suggesting it is least aligned with current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_sync_index = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy = entropy_scores[key]
        sync_index = sync_indices[key]
        
        if entropy > max_entropy or (entropy == max_entropy and sync_index < min_sync_index):
            max_entropy = entropy
            min_sync_index = sync_index
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal vector of the accessed entry is updated to reflect the recent access, reducing its entropy score. The synchronization index is adjusted to better align with the current system-wide access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    temporal_vector = temporal_vectors[obj.key]
    temporal_vector.append(cache_snapshot.access_count)
    entropy_scores[obj.key] = calculate_entropy(temporal_vector)
    sync_indices[obj.key] += SYNC_INDEX_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its temporal vector is initialized based on recent access patterns, and its entropy score is set to a default high value. The synchronization index is calibrated to align with the current system trend.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    temporal_vectors[obj.key] = deque([cache_snapshot.access_count] * TEMPORAL_VECTOR_SIZE, maxlen=TEMPORAL_VECTOR_SIZE)
    entropy_scores[obj.key] = DEFAULT_ENTROPY_SCORE
    sync_indices[obj.key] = cache_snapshot.access_count * SYNC_INDEX_ADJUSTMENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the synchronization indices of remaining entries to ensure alignment with the updated system-wide access trends, and adjusts their entropy scores to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del temporal_vectors[evicted_obj.key]
    del entropy_scores[evicted_obj.key]
    del sync_indices[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        sync_indices[key] *= (1 - SYNC_INDEX_ADJUSTMENT_FACTOR)
        entropy_scores[key] = calculate_entropy(temporal_vectors[key])
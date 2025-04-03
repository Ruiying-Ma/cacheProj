# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
BASELINE_RESILIENCE_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a sequence history of access patterns, a predictive resilience score for each cache entry, a consistency layer to ensure data integrity, and an optimized index for quick lookup and updates.
sequence_history = deque()  # To maintain access patterns
resilience_scores = defaultdict(lambda: BASELINE_RESILIENCE_SCORE)  # Predictive resilience scores
consistency_layer = set()  # To ensure data integrity
optimized_index = {}  # For quick lookup and updates

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by analyzing the adaptive sequence history to predict future access patterns, selecting the entry with the lowest predictive resilience score while ensuring consistency is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_resilience_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if resilience_scores[key] < min_resilience_score:
            min_resilience_score = resilience_scores[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequence history is updated to reflect the latest access, the predictive resilience score of the accessed entry is increased, and the consistency layer is checked to ensure data integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    sequence_history.append(obj.key)
    resilience_scores[obj.key] += 1
    consistency_layer.add(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequence history is updated to include the new entry, a baseline predictive resilience score is assigned, and the optimized index is adjusted for efficient future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    sequence_history.append(obj.key)
    resilience_scores[obj.key] = BASELINE_RESILIENCE_SCORE
    optimized_index[obj.key] = obj

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the sequence history is pruned to remove the evicted entry, the predictive resilience scores are recalibrated, and the consistency layer is verified to ensure no stale data remains.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    sequence_history.remove(evicted_obj.key)
    del resilience_scores[evicted_obj.key]
    consistency_layer.discard(evicted_obj.key)
    if evicted_obj.key in optimized_index:
        del optimized_index[evicted_obj.key]
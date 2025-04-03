# Import anything you need below
from collections import deque

# Put tunable constant parameters below
PREDICTIVE_SCORE_INCREMENT = 1
INITIAL_PREDICTIVE_SCORE = 5
COHERENCE_STABLE = 1
COHERENCE_UNSTABLE = 0
EVICTION_CANDIDATE_COUNT = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue for order tracking and a metadata set for each cache entry, including a predictive score and a coherence score. The predictive score is based on a heuristic model, while the coherence score is a binary flag indicating data stability.
fifo_queue = deque()
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a subset of cache entries from the front of the FIFO queue and evicts the one with the lowest combined predictive and coherence score, ensuring a balance between temporal order and informed decision-making.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    candidates = list(fifo_queue)[:EVICTION_CANDIDATE_COUNT]
    min_score = float('inf')
    
    for key in candidates:
        pred_score, coherence_score = metadata[key]
        combined_score = pred_score + coherence_score
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is slightly increased to reflect its relevance, the coherence score is toggled to indicate increased stability, and the entry is moved to the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in metadata:
        pred_score, coherence_score = metadata[key]
        metadata[key] = (pred_score + PREDICTIVE_SCORE_INCREMENT, 1 - coherence_score)
        fifo_queue.remove(key)
        fifo_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized using a simple heuristic, the coherence score is set to unstable, and the object is placed at the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key] = (INITIAL_PREDICTIVE_SCORE, COHERENCE_UNSTABLE)
    fifo_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive model is lightly recalibrated to improve future predictions, the coherence framework is adjusted to reflect the new data stability landscape, and the evicted object is removed from the front of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
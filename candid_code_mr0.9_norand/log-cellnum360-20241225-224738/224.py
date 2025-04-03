# Import anything you need below
from collections import deque

# Put tunable constant parameters below
PREDICTIVE_SCORE_INCREMENT = 0.1
INITIAL_PREDICTIVE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, access frequency, a predictive score, and a coherence score for each cached object. The access frequency is an integer, the predictive score is a heuristic-based value, and the coherence score is a binary flag.
fifo_queue = deque()
access_frequency = {}
predictive_score = {}
coherence_score = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a subset of cache entries starting from the current pointer position and evaluates their combined access frequency, predictive score, and coherence score. The object with the lowest combined score is evicted, and the pointer moves to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in fifo_queue:
        combined_score = (access_frequency[key] + 
                          predictive_score[key] + 
                          coherence_score[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is set to 1, the predictive score is slightly increased, and the coherence score is toggled to indicate increased stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    predictive_score[key] += PREDICTIVE_SCORE_INCREMENT
    coherence_score[key] = 1 - coherence_score[key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its access frequency is set to 1, the predictive score is initialized using a heuristic, and the coherence score is set to unstable. The object is placed at the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    predictive_score[key] = INITIAL_PREDICTIVE_SCORE
    coherence_score[key] = 0
    fifo_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive model is lightly recalibrated, the coherence framework is adjusted, and the FIFO queue is updated to remove the evicted object and shift remaining objects forward.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    fifo_queue.remove(evicted_key)
    del access_frequency[evicted_key]
    del predictive_score[evicted_key]
    del coherence_score[evicted_key]
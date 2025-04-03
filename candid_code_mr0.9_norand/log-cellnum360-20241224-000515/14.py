# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
DECAY_FACTOR = 0.9
INCREMENT_FACTOR = 1.1
MH_LIST_SIZE = 5
BASELINE_RETROACTIVE_SCORE = 1.0
BASELINE_FUTURE_PREDICTION_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a retroactive score for each cache entry, which is a weighted sum of past access frequencies and recency, adjusted by a decay factor. It also keeps a future access prediction score based on historical patterns and a minimal history (MH) list of recently evicted items to adjust predictions.
retroactive_scores = defaultdict(lambda: BASELINE_RETROACTIVE_SCORE)
future_prediction_scores = defaultdict(lambda: BASELINE_FUTURE_PREDICTION_SCORE)
mh_list = deque(maxlen=MH_LIST_SIZE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined retroactive and future access prediction score. This approach aims to approximate the optimal page replacement by considering both past and predicted future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (retroactive_scores[key] + future_prediction_scores[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the retroactive score of the accessed entry is increased based on its current score and a predefined increment factor, while the future access prediction score is adjusted upwards slightly to reflect the increased likelihood of future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    retroactive_scores[key] *= INCREMENT_FACTOR
    future_prediction_scores[key] += 0.1  # Slight increase to reflect future access likelihood

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its retroactive score to a baseline value and calculates an initial future access prediction score using patterns from the MH list. The MH list is updated to include the newly inserted object, maintaining a fixed size by removing the oldest entry if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    retroactive_scores[key] = BASELINE_RETROACTIVE_SCORE
    future_prediction_scores[key] = BASELINE_FUTURE_PREDICTION_SCORE
    
    # Update MH list
    mh_list.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy adds the evicted entry to the MH list, updating the list to reflect recent eviction patterns. The retroactive scores of remaining entries are decayed slightly to reflect the passage of time and potential changes in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    mh_list.append(evicted_key)
    
    # Decay retroactive scores
    for key in cache_snapshot.cache:
        retroactive_scores[key] *= DECAY_FACTOR
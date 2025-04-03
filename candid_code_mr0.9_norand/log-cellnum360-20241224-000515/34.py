# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
LATENCY_THRESHOLD = 5
INITIAL_PREDICTIVE_SCORE = 10
BASELINE_LATENCY_SCORE = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a rotation index for cache blocks, a predictive score for each block based on access patterns, a serialization queue for adaptive ordering, and a latency score for each block to optimize access times.
rotation_index = 0
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
serialization_queue = deque()
latency_scores = defaultdict(lambda: BASELINE_LATENCY_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the block with the lowest predictive score, considering the current rotation index, and ensuring that the block's latency score is above a certain threshold to avoid evicting frequently accessed blocks.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if predictive_scores[key] < min_score and latency_scores[key] > LATENCY_THRESHOLD:
            min_score = predictive_scores[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the predictive score of the accessed block, updates its position in the serialization queue to reflect recent access, and adjusts its latency score to reflect improved access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] += 1
    latency_scores[key] -= 1
    
    if key in serialization_queue:
        serialization_queue.remove(key)
    serialization_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns, places it at the end of the serialization queue, and assigns a baseline latency score to start tracking its access efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] = INITIAL_PREDICTIVE_SCORE
    latency_scores[key] = BASELINE_LATENCY_SCORE
    serialization_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a block, the policy rotates the rotation index to the next position, recalibrates the predictive scores of remaining blocks to reflect the new cache state, and updates the serialization queue to remove the evicted block.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global rotation_index
    rotation_index = (rotation_index + 1) % len(cache_snapshot.cache)
    
    evicted_key = evicted_obj.key
    if evicted_key in serialization_queue:
        serialization_queue.remove(evicted_key)
    
    for key in cache_snapshot.cache:
        predictive_scores[key] = max(1, predictive_scores[key] - 1)
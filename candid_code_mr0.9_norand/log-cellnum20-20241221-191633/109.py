# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
SCORE_INCREMENT_ON_HIT = 1.0
LOAD_BALANCE_FACTOR = 0.1
DYNAMIC_SCALING_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry based on historical access patterns, a load balancing factor to distribute cache load evenly, a dynamic scaling factor to adjust cache size based on current demand, and an adaptive queue to manage cache entries based on their predicted future access.
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
adaptive_queue = deque()
load_balancing_factor = LOAD_BALANCE_FACTOR
dynamic_scaling_factor = DYNAMIC_SCALING_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, adjusted by the load balancing factor and dynamic scaling factor, ensuring that the cache remains balanced and responsive to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = (predictive_scores[key] * load_balancing_factor) / dynamic_scaling_factor
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is increased, the load balancing factor is adjusted to reflect the current access load, and the entry is repositioned in the adaptive queue to reflect its increased likelihood of future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    predictive_scores[obj.key] += SCORE_INCREMENT_ON_HIT
    load_balancing_factor = cache_snapshot.access_count / (cache_snapshot.hit_count + 1)
    
    if obj.key in adaptive_queue:
        adaptive_queue.remove(obj.key)
    adaptive_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial predictive score based on similar past entries, updates the load balancing factor to account for the new entry, and places the entry in the adaptive queue according to its initial score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    predictive_scores[obj.key] = INITIAL_PREDICTIVE_SCORE
    load_balancing_factor = cache_snapshot.access_count / (cache_snapshot.hit_count + 1)
    adaptive_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries, adjusts the load balancing factor to reflect the reduced cache load, and reorders the adaptive queue to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in predictive_scores:
        del predictive_scores[evicted_obj.key]
    
    load_balancing_factor = cache_snapshot.access_count / (cache_snapshot.hit_count + 1)
    
    if evicted_obj.key in adaptive_queue:
        adaptive_queue.remove(evicted_obj.key)
    
    # Reorder adaptive queue based on updated predictive scores
    adaptive_queue_sorted = sorted(adaptive_queue, key=lambda k: predictive_scores[k])
    adaptive_queue.clear()
    adaptive_queue.extend(adaptive_queue_sorted)
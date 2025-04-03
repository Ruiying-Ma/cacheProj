# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import heapq

# Put tunable constant parameters below
INITIAL_TEMPORAL_LOCALITY_SCORE = 1
INITIAL_PROBABILISTIC_WEIGHT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue for cache lines based on a combination of temporal locality scores and probabilistic eviction weights. It also tracks coherence states to ensure consistency across multiple caches.
priority_queue = []
temporal_locality_scores = {}
probabilistic_weights = {}
coherence_states = {}

def calculate_priority_score(key):
    return temporal_locality_scores[key] * probabilistic_weights[key]

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the lowest priority score from the priority queue, which is determined by a weighted combination of its temporal locality score and a probabilistic factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        _, candid_obj_key = heapq.heappop(priority_queue)
        if candid_obj_key in cache_snapshot.cache:
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the temporal locality score of the accessed cache line is increased, and its position in the priority queue is updated accordingly. The coherence state is also checked and updated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_locality_scores[key] += 1
    heapq.heappush(priority_queue, (calculate_priority_score(key), key))
    # Update coherence state if necessary
    coherence_states[key] = 'updated'

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial temporal locality score and a probabilistic eviction weight to the new cache line, then inserts it into the priority queue. The coherence state is initialized to ensure consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_locality_scores[key] = INITIAL_TEMPORAL_LOCALITY_SCORE
    probabilistic_weights[key] = INITIAL_PROBABILISTIC_WEIGHT
    heapq.heappush(priority_queue, (calculate_priority_score(key), key))
    # Initialize coherence state
    coherence_states[key] = 'initialized'

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a cache line, the policy removes it from the priority queue and updates the coherence state to reflect the eviction. The temporal locality scores and probabilistic weights of remaining cache lines may be adjusted to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in temporal_locality_scores:
        del temporal_locality_scores[evicted_key]
    if evicted_key in probabilistic_weights:
        del probabilistic_weights[evicted_key]
    if evicted_key in coherence_states:
        del coherence_states[evicted_key]
    # Adjust remaining cache lines if necessary
    for key in cache_snapshot.cache:
        heapq.heappush(priority_queue, (calculate_priority_score(key), key))
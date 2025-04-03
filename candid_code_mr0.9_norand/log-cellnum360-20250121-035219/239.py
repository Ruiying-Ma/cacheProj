# Import anything you need below
import collections

# Put tunable constant parameters below
HIT_RATE_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive cache hit rate for each object, an adaptive queue for managing objects based on their access patterns, a dynamic load balancing factor to distribute cache space efficiently, and statistical access patterns to track frequency and recency of accesses.
predictive_cache_hit_rate = {}
adaptive_queue = collections.deque()
dynamic_load_balancing_factor = 1.0
access_frequency = collections.defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest predictive cache hit rate, adjusted by the dynamic load balancing factor and the object's position in the adaptive queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        hit_rate = predictive_cache_hit_rate.get(key, 0)
        position = adaptive_queue.index(key) if key in adaptive_queue else len(adaptive_queue)
        score = hit_rate * dynamic_load_balancing_factor + position
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the predictive cache hit rate by increasing it slightly, adjusts the object's position in the adaptive queue to reflect its recent access, and recalculates the dynamic load balancing factor to ensure efficient space distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_cache_hit_rate[key] = predictive_cache_hit_rate.get(key, 0) + HIT_RATE_INCREMENT
    if key in adaptive_queue:
        adaptive_queue.remove(key)
    adaptive_queue.appendleft(key)
    access_frequency[key] += 1
    recalculate_dynamic_load_balancing_factor(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive cache hit rate, places it in the adaptive queue based on its initial access pattern, and updates the dynamic load balancing factor to account for the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_cache_hit_rate[key] = 0
    adaptive_queue.appendleft(key)
    access_frequency[key] = 1
    recalculate_dynamic_load_balancing_factor(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes its metadata, recalculates the dynamic load balancing factor to redistribute the freed space, and adjusts the adaptive queue to maintain optimal management of the remaining objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in predictive_cache_hit_rate:
        del predictive_cache_hit_rate[evicted_key]
    if evicted_key in adaptive_queue:
        adaptive_queue.remove(evicted_key)
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    recalculate_dynamic_load_balancing_factor(cache_snapshot)

def recalculate_dynamic_load_balancing_factor(cache_snapshot):
    '''
    Recalculates the dynamic load balancing factor to ensure efficient space distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
    - Return: `None`
    '''
    if cache_snapshot.size == 0:
        dynamic_load_balancing_factor = 1.0
    else:
        dynamic_load_balancing_factor = cache_snapshot.capacity / cache_snapshot.size
# Import anything you need below
import collections

# Put tunable constant parameters below
INITIAL_FREQUENCY = 1
INITIAL_LATENCY = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a state latency vector for each cache line, a dynamic shift counter, an allocation vector indicating the frequency of accesses, and a predictive balance score for each cache line.
state_latency = collections.defaultdict(lambda: INITIAL_LATENCY)
dynamic_shift_counter = 0
allocation_vector = collections.defaultdict(lambda: INITIAL_FREQUENCY)
predictive_balance_score = collections.defaultdict(lambda: 0)

def calculate_predictive_balance_score(key):
    return state_latency[key] + dynamic_shift_counter - allocation_vector[key]

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the highest predictive balance score, which is calculated based on the state latency and dynamic shift values, indicating the least likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = float('-inf')
    
    for key in cache_snapshot.cache:
        score = calculate_predictive_balance_score(key)
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the state latency vector for the accessed cache line is updated to reflect the current latency, the dynamic shift counter is incremented, and the allocation vector is adjusted to increase the frequency count. The predictive balance score is recalculated based on the new values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global dynamic_shift_counter
    
    key = obj.key
    state_latency[key] = cache_snapshot.access_count
    dynamic_shift_counter += 1
    allocation_vector[key] += 1
    predictive_balance_score[key] = calculate_predictive_balance_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the state latency vector is initialized, the dynamic shift counter is reset, the allocation vector is updated to include the new object with an initial frequency count, and the predictive balance score is set based on initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global dynamic_shift_counter
    
    key = obj.key
    state_latency[key] = cache_snapshot.access_count
    dynamic_shift_counter = 0
    allocation_vector[key] = INITIAL_FREQUENCY
    predictive_balance_score[key] = calculate_predictive_balance_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the state latency vector, dynamic shift counter, and allocation vector are updated to remove the evicted cache line's data. The predictive balance scores for remaining cache lines are recalculated to reflect the new state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    
    del state_latency[key]
    del allocation_vector[key]
    del predictive_balance_score[key]
    
    for key in cache_snapshot.cache:
        predictive_balance_score[key] = calculate_predictive_balance_score(key)
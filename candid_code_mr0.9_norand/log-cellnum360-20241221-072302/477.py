# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENT_ACCESS_THRESHOLD = 5  # Number of accesses to consider an object frequently accessed
PREDICTIVE_DECAY = 0.9  # Decay factor for predictive model

# Put the metadata specifically maintained by the policy below. The policy maintains a finite state machine for each cache line, tracking states such as 'frequently accessed', 'recently accessed', and 'infrequently accessed'. It also keeps a predictive model of access patterns using loop unrolling techniques to anticipate future accesses.
cache_states = defaultdict(lambda: 'infrequently accessed')
access_counts = defaultdict(int)
predictive_model = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying cache lines in the 'infrequently accessed' state with the lowest predicted future access probability, effectively inverting latency by preemptively removing lines unlikely to be needed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_predicted_access = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if cache_states[key] == 'infrequently accessed':
            if predictive_model[key] < min_predicted_access:
                min_predicted_access = predictive_model[key]
                candid_obj_key = key
    
    if candid_obj_key is None:
        # If no infrequently accessed object is found, fall back to evicting the least predicted access
        for key, cached_obj in cache_snapshot.cache.items():
            if predictive_model[key] < min_predicted_access:
                min_predicted_access = predictive_model[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the state of the accessed line is updated to 'frequently accessed', and the predictive model is adjusted to increase the probability of future accesses to this line, enhancing algorithmic resilience.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_counts[obj.key] += 1
    if access_counts[obj.key] >= FREQUENT_ACCESS_THRESHOLD:
        cache_states[obj.key] = 'frequently accessed'
    
    # Update predictive model
    predictive_model[obj.key] = min(1.0, predictive_model[obj.key] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its state to 'recently accessed' and updates the predictive model to reflect a potential increase in access frequency, preparing the system for potential future hits.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_states[obj.key] = 'recently accessed'
    access_counts[obj.key] = 1
    predictive_model[obj.key] = 0.5  # Initial prediction for new objects

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive model to reduce the predicted access probability of similar patterns, and the state machine transitions to reflect the removal, ensuring the system adapts to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Reduce the predicted access probability of the evicted object
    predictive_model[evicted_obj.key] *= PREDICTIVE_DECAY
    # Remove the evicted object from the state and access count tracking
    del cache_states[evicted_obj.key]
    del access_counts[evicted_obj.key]
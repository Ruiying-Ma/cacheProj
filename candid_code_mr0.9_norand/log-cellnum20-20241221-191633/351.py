# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1
NEUTRAL_ADAPTIVE_SCORE = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive queue for each cache entry, a priority level for each entry, a consistency state flag, and an adaptive response score. The predictive queue estimates future access patterns, the priority level indicates the importance of the entry, the consistency state ensures data integrity, and the adaptive response score adjusts based on system performance.
predictive_queues = defaultdict(deque)
priority_levels = defaultdict(lambda: DEFAULT_PRIORITY)
consistency_states = defaultdict(lambda: True)
adaptive_response_scores = defaultdict(lambda: NEUTRAL_ADAPTIVE_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority level and the least predicted future access from the predictive queue. If a tie occurs, the entry with the lowest adaptive response score is evicted, ensuring state consistency is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    min_predicted_access = float('inf')
    min_adaptive_score = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_levels[key]
        predicted_access = len(predictive_queues[key])
        adaptive_score = adaptive_response_scores[key]

        if (priority < min_priority or
            (priority == min_priority and predicted_access < min_predicted_access) or
            (priority == min_priority and predicted_access == min_predicted_access and adaptive_score < min_adaptive_score)):
            min_priority = priority
            min_predicted_access = predicted_access
            min_adaptive_score = adaptive_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive queue for the accessed entry is updated to reflect the new access pattern, the priority level is increased, the consistency state is checked and updated if necessary, and the adaptive response score is adjusted to reflect improved performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Update predictive queue
    predictive_queues[key].append(cache_snapshot.access_count)
    # Increase priority level
    priority_levels[key] += 1
    # Check and update consistency state
    consistency_states[key] = True  # Assuming consistency is maintained
    # Adjust adaptive response score
    adaptive_response_scores[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive queue is initialized based on initial access predictions, the priority level is set to a default value, the consistency state is marked as consistent, and the adaptive response score is set to a neutral value to allow for future adjustments.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Initialize predictive queue
    predictive_queues[key] = deque([cache_snapshot.access_count])
    # Set priority level to default
    priority_levels[key] = DEFAULT_PRIORITY
    # Mark consistency state as consistent
    consistency_states[key] = True
    # Set adaptive response score to neutral
    adaptive_response_scores[key] = NEUTRAL_ADAPTIVE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive queues of remaining entries are recalibrated to account for the change in cache composition, priority levels are adjusted to reflect the new cache state, the consistency state of all entries is verified, and the adaptive response score is updated to reflect the impact of the eviction on system performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate predictive queues
    for key in cache_snapshot.cache:
        predictive_queues[key].append(cache_snapshot.access_count)
    
    # Adjust priority levels
    for key in cache_snapshot.cache:
        priority_levels[key] = max(DEFAULT_PRIORITY, priority_levels[key] - 1)
    
    # Verify consistency state
    for key in cache_snapshot.cache:
        consistency_states[key] = True  # Assuming consistency is maintained
    
    # Update adaptive response scores
    for key in cache_snapshot.cache:
        adaptive_response_scores[key] -= 1
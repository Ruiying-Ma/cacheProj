# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FEEDBACK_SCORE = 1
QUANTIZED_LEVEL_INCREMENT = 1
FEEDBACK_SCORE_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a synchronization drift counter for each cache entry, an evolutionary feedback score, and a quantized interface level. The synchronization drift counter tracks the time since the last access, the evolutionary feedback score adapts based on access patterns, and the quantized interface level represents the cache entry's predicted future utility.
sync_drift_counter = defaultdict(int)
evolutionary_feedback_score = defaultdict(lambda: BASELINE_FEEDBACK_SCORE)
quantized_interface_level = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest synchronization drift counter, adjusted by the evolutionary feedback score and quantized interface level. This ensures that entries with low predicted future utility and high drift are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (sync_drift_counter[key] - 
                 evolutionary_feedback_score[key] - 
                 quantized_interface_level[key])
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the synchronization drift counter is reset, the evolutionary feedback score is incremented to reflect the positive access pattern, and the quantized interface level is adjusted upwards to increase the predicted future utility of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    sync_drift_counter[key] = 0
    evolutionary_feedback_score[key] += FEEDBACK_SCORE_INCREMENT
    quantized_interface_level[key] += QUANTIZED_LEVEL_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the synchronization drift counter is initialized to zero, the evolutionary feedback score is set to a neutral baseline, and the quantized interface level is calculated based on initial predictive tuning using historical access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    sync_drift_counter[key] = 0
    evolutionary_feedback_score[key] = BASELINE_FEEDBACK_SCORE
    quantized_interface_level[key] = 0  # Initial predictive tuning can be more complex

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the evolutionary feedback scores of remaining entries to reflect the change in cache dynamics and adjusts the quantized interface levels to ensure accurate predictive tuning for future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        # Recalibrate feedback scores and quantized levels
        evolutionary_feedback_score[key] = max(BASELINE_FEEDBACK_SCORE, evolutionary_feedback_score[key] - 1)
        quantized_interface_level[key] = max(0, quantized_interface_level[key] - 1)
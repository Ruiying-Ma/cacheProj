# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
TEMPORAL_DECAY_FACTOR = 0.9
PARTITION_WEIGHT_ADJUSTMENT = 0.1
CONSISTENCY_BUFFER_SIZE = 5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each cache entry, a temporal access pattern log, partition weights for different cache regions, and a consistency buffer to track recent changes.
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
temporal_logs = defaultdict(deque)
partition_weights = defaultdict(lambda: 1.0)
consistency_buffer = deque(maxlen=CONSISTENCY_BUFFER_SIZE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, adjusted by its temporal efficiency and partition weight, ensuring that the consistency buffer is not violated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if key in consistency_buffer:
            continue
        
        adjusted_score = (predictive_scores[key] * 
                          partition_weights[key] * 
                          (TEMPORAL_DECAY_FACTOR ** len(temporal_logs[key])))
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is refined based on recent access patterns, its temporal log is updated, and the consistency buffer is checked to ensure recent changes are consistent.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] += 1
    temporal_logs[key].append(cache_snapshot.access_count)
    consistency_buffer.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns, updates the temporal log, adjusts partition weights to accommodate the new entry, and logs the change in the consistency buffer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] = INITIAL_PREDICTIVE_SCORE
    temporal_logs[key].append(cache_snapshot.access_count)
    partition_weights[key] += PARTITION_WEIGHT_ADJUSTMENT
    consistency_buffer.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries, updates the temporal logs to reflect the change, adjusts partition weights to optimize space, and clears the relevant entry from the consistency buffer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in predictive_scores:
        del predictive_scores[evicted_key]
    if evicted_key in temporal_logs:
        del temporal_logs[evicted_key]
    if evicted_key in partition_weights:
        del partition_weights[evicted_key]
    if evicted_key in consistency_buffer:
        consistency_buffer.remove(evicted_key)
    
    for key in cache_snapshot.cache:
        predictive_scores[key] *= TEMPORAL_DECAY_FACTOR
        partition_weights[key] = max(1.0, partition_weights[key] - PARTITION_WEIGHT_ADJUSTMENT)
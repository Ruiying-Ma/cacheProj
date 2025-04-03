# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY = 1
PRIORITY_ESCALATION_THRESHOLD = 3
TEMPORAL_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a batch access counter, a temporal access pattern score, a priority level for each cache entry, and a predictive score based on historical access patterns.
batch_access_counter = defaultdict(int)
temporal_access_pattern_score = defaultdict(float)
priority_level = defaultdict(int)
predictive_score = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined score of temporal access pattern and predictive score, while considering priority escalation to retain high-priority items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (temporal_access_pattern_score[key] + predictive_score[key]) / (priority_level[key] + 1)
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the batch access counter is incremented, the temporal access pattern score is updated based on recent access frequency, and the priority level is escalated if the item is accessed multiple times within a short period.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    batch_access_counter[key] += 1
    temporal_access_pattern_score[key] = TEMPORAL_DECAY_FACTOR * temporal_access_pattern_score[key] + 1
    
    if batch_access_counter[key] >= PRIORITY_ESCALATION_THRESHOLD:
        priority_level[key] += 1
        batch_access_counter[key] = 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the batch access counter is initialized, the temporal access pattern score is set based on initial access predictions, and the priority level is assigned based on the object's importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    batch_access_counter[key] = 0
    temporal_access_pattern_score[key] = 1  # Initial prediction
    priority_level[key] = INITIAL_PRIORITY
    predictive_score[key] = 0  # Initial predictive score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the batch access counter is reset, the temporal access pattern score is adjusted to reflect the removal, and the priority level is recalibrated for remaining items to ensure balance in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del batch_access_counter[evicted_key]
    del temporal_access_pattern_score[evicted_key]
    del priority_level[evicted_key]
    del predictive_score[evicted_key]
    
    # Recalibrate priority levels for remaining items
    for key in cache_snapshot.cache:
        priority_level[key] = max(INITIAL_PRIORITY, priority_level[key] - 1)
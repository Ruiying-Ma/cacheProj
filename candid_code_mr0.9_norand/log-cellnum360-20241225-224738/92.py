# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TEMPORAL_ALIGNMENT = 1
INITIAL_EFFICIENCY_SCORE = 1
PROMOTION_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of cache blocks, each with a temporal alignment score and an efficiency score. The temporal alignment score tracks the recency and frequency of access, while the efficiency score measures the cost-benefit ratio of retaining the block.
temporal_alignment_scores = defaultdict(lambda: INITIAL_TEMPORAL_ALIGNMENT)
efficiency_scores = defaultdict(lambda: INITIAL_EFFICIENCY_SCORE)
hierarchy_levels = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying the lowest hierarchy level with the least temporal alignment. Within this level, it selects the block with the lowest efficiency score, ensuring strategic recalibration by occasionally promoting blocks with potential future value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_level = min(hierarchy_levels.values())
    candidates = [key for key, level in hierarchy_levels.items() if level == min_level]
    
    if candidates:
        candid_obj_key = min(candidates, key=lambda k: efficiency_scores[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal alignment score of the accessed block is increased to reflect its recent use, and its efficiency score is recalibrated to account for the reduced cost of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    temporal_alignment_scores[obj.key] += 1
    efficiency_scores[obj.key] = max(1, efficiency_scores[obj.key] - 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial temporal alignment score based on predicted access patterns and an efficiency score based on the expected cost-benefit ratio, integrating it into the appropriate hierarchy level.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    temporal_alignment_scores[obj.key] = INITIAL_TEMPORAL_ALIGNMENT
    efficiency_scores[obj.key] = INITIAL_EFFICIENCY_SCORE
    hierarchy_levels[obj.key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the hierarchy by adjusting the temporal alignment and efficiency scores of neighboring blocks, promoting those with improved potential to higher levels to boost overall cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del temporal_alignment_scores[evicted_obj.key]
    del efficiency_scores[evicted_obj.key]
    del hierarchy_levels[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        if temporal_alignment_scores[key] > PROMOTION_THRESHOLD:
            hierarchy_levels[key] += 1
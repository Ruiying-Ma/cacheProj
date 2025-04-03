# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SCORE = 1
SCORE_INCREMENT = 1
RECENT_ACCESS_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic overlay map that tracks access patterns, temporal anchors that record the last access time, predictive streamline scores for future access likelihood, and contextual disjunction flags that indicate the relevance of data in different contexts.
temporal_anchors = {}
predictive_scores = defaultdict(lambda: BASELINE_SCORE)
contextual_flags = defaultdict(lambda: True)  # Assume all objects are relevant initially

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the item with the lowest predictive streamline score, considering the temporal anchor to ensure it hasn't been accessed recently, and checking contextual disjunction flags to ensure it is not relevant in the current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        if not contextual_flags[key]:
            continue
        if cache_snapshot.access_count - temporal_anchors[key] < RECENT_ACCESS_THRESHOLD:
            continue
        if predictive_scores[key] < min_score:
            min_score = predictive_scores[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the temporal anchor to the current time, increases the predictive streamline score based on recent access patterns, and adjusts the contextual disjunction flags to reflect the current context's relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    temporal_anchors[obj.key] = cache_snapshot.access_count
    predictive_scores[obj.key] += SCORE_INCREMENT
    contextual_flags[obj.key] = True  # Assume context is relevant after a hit

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal anchor to the current time, assigns a baseline predictive streamline score, and sets contextual disjunction flags based on the initial context of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    temporal_anchors[obj.key] = cache_snapshot.access_count
    predictive_scores[obj.key] = BASELINE_SCORE
    contextual_flags[obj.key] = True  # Assume context is relevant upon insertion

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic overlay map to remove the evicted item's influence, adjusts predictive streamline scores of remaining items to reflect the change, and updates contextual disjunction flags to ensure they remain accurate for the current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove evicted object's metadata
    if evicted_obj.key in temporal_anchors:
        del temporal_anchors[evicted_obj.key]
    if evicted_obj.key in predictive_scores:
        del predictive_scores[evicted_obj.key]
    if evicted_obj.key in contextual_flags:
        del contextual_flags[evicted_obj.key]

    # Adjust scores and flags for remaining items
    for key in cache_snapshot.cache:
        predictive_scores[key] = max(BASELINE_SCORE, predictive_scores[key] - SCORE_INCREMENT)
        contextual_flags[key] = True  # Re-evaluate context relevance
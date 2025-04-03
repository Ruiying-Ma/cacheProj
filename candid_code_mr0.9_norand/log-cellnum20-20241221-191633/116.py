# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_WEIGHT = 0.4
TEMPORAL_WEIGHT = 0.4
ADAPTIVE_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each object based on access patterns, a resource scaling factor indicating the current cache size, a temporal score reflecting recent access frequency, and an adaptive feedback score that adjusts based on past eviction success.
predictive_scores = defaultdict(lambda: 1.0)
temporal_scores = defaultdict(lambda: 1.0)
adaptive_feedback_scores = defaultdict(lambda: 1.0)
resource_scaling_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object, which is a weighted sum of the predictive score, temporal score, and adaptive feedback score. The object with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (PREDICTIVE_WEIGHT * predictive_scores[key] +
                           TEMPORAL_WEIGHT * temporal_scores[key] +
                           ADAPTIVE_WEIGHT * adaptive_feedback_scores[key])
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score is updated based on the accuracy of past predictions, the temporal score is incremented to reflect recent access, and the adaptive feedback score is adjusted to reinforce successful retention decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] *= 1.1  # Increase predictive score slightly
    temporal_scores[key] += 1  # Increment temporal score
    adaptive_feedback_scores[key] *= 1.05  # Slightly reinforce adaptive feedback

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized based on historical data or default values, the temporal score is set to a baseline reflecting initial access, and the adaptive feedback score is adjusted to account for the new object's potential impact on cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] = 1.0  # Initialize predictive score
    temporal_scores[key] = 1.0  # Set baseline temporal score
    adaptive_feedback_scores[key] = 1.0  # Initialize adaptive feedback score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive score of remaining objects is recalibrated to improve future predictions, the resource scaling factor is adjusted to reflect the new cache size, and the adaptive feedback score is updated to learn from the eviction outcome, enhancing future decision-making.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        predictive_scores[key] *= 0.95  # Recalibrate predictive scores

    global resource_scaling_factor
    resource_scaling_factor = cache_snapshot.size / cache_snapshot.capacity

    adaptive_feedback_scores[evicted_obj.key] *= 0.9  # Learn from eviction
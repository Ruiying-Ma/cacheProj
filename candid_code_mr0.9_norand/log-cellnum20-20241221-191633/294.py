# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_SCORE_INIT = 1.0
PRIORITY_LEVEL_INIT = 1.0
TEMPORAL_SYNTHESIS_INIT = 1.0
EVENT_DRIVEN_FLAG_INIT = False

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each cache entry, a priority level based on access frequency and recency, a temporal synthesis score that combines time-based patterns, and an event-driven flag indicating recent system events affecting cache behavior.
metadata = {
    'predictive_score': defaultdict(lambda: PREDICTIVE_SCORE_INIT),
    'priority_level': defaultdict(lambda: PRIORITY_LEVEL_INIT),
    'temporal_synthesis': defaultdict(lambda: TEMPORAL_SYNTHESIS_INIT),
    'event_driven_flag': defaultdict(lambda: EVENT_DRIVEN_FLAG_INIT)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of predictive caching and priority adaptation, while also considering temporal synthesis to avoid evicting entries likely to be accessed soon. Event-driven flags are checked to adjust the decision based on recent system events.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (metadata['predictive_score'][key] + 
                          metadata['priority_level'][key] - 
                          metadata['temporal_synthesis'][key])
        
        if metadata['event_driven_flag'][key]:
            combined_score *= 0.9  # Adjust score if event-driven flag is set
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score is increased based on the accuracy of past predictions, the priority level is boosted to reflect increased access frequency, the temporal synthesis score is adjusted to reflect the current time pattern, and the event-driven flag is updated if the hit correlates with recent system events.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_score'][key] += 0.1  # Increase predictive score
    metadata['priority_level'][key] += 1.0   # Boost priority level
    metadata['temporal_synthesis'][key] = cache_snapshot.access_count % 10  # Adjust temporal synthesis
    metadata['event_driven_flag'][key] = True  # Update event-driven flag

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized based on historical data or default values, the priority level is set to a baseline reflecting initial access, the temporal synthesis score is calculated based on current time patterns, and the event-driven flag is set according to any relevant system events at the time of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_score'][key] = PREDICTIVE_SCORE_INIT
    metadata['priority_level'][key] = PRIORITY_LEVEL_INIT
    metadata['temporal_synthesis'][key] = cache_snapshot.access_count % 10
    metadata['event_driven_flag'][key] = EVENT_DRIVEN_FLAG_INIT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive scores of remaining entries are recalibrated to reflect the change in cache composition, priority levels are adjusted to account for the removal of the evicted entry, temporal synthesis scores are updated to reflect the new temporal dynamics, and event-driven flags are reset or adjusted based on the impact of the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['predictive_score'][evicted_key]
    del metadata['priority_level'][evicted_key]
    del metadata['temporal_synthesis'][evicted_key]
    del metadata['event_driven_flag'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] *= 0.95  # Recalibrate predictive scores
        metadata['priority_level'][key] *= 0.95   # Adjust priority levels
        metadata['temporal_synthesis'][key] = cache_snapshot.access_count % 10  # Update temporal synthesis
        metadata['event_driven_flag'][key] = False  # Reset event-driven flags
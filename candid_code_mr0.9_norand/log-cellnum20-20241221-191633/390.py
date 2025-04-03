# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
FREQUENCY_BOOST = 1.5
TEMPORAL_DECAY_FACTOR = 0.9
INITIAL_FREQUENCY = 1.0
INITIAL_TEMPORAL_DECAY = 1.0
INITIAL_PREDICTIVE_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, which is a composite of temporal recency, access frequency, and a predictive score based on access patterns. It also tracks a temporal decay factor that adjusts the priority score over time.
cache_metadata = {
    'frequency': defaultdict(lambda: INITIAL_FREQUENCY),
    'temporal_decay': defaultdict(lambda: INITIAL_TEMPORAL_DECAY),
    'predictive_score': defaultdict(lambda: INITIAL_PREDICTIVE_SCORE),
    'priority_score': defaultdict(float)
}

def calculate_priority_score(key):
    frequency = cache_metadata['frequency'][key]
    temporal_decay = cache_metadata['temporal_decay'][key]
    predictive_score = cache_metadata['predictive_score'][key]
    return frequency * temporal_decay * predictive_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest priority score. This score is dynamically adjusted by the temporal decay and frequency modulation, ensuring that less frequently accessed and older entries are more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key in cache_snapshot.cache:
        priority_score = calculate_priority_score(key)
        if priority_score < min_priority_score:
            min_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased by boosting its frequency component and resetting its temporal decay factor. The predictive score is also updated based on recent access patterns to anticipate future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] *= FREQUENCY_BOOST
    cache_metadata['temporal_decay'][key] = INITIAL_TEMPORAL_DECAY
    # Update predictive score based on some heuristic or pattern recognition
    cache_metadata['predictive_score'][key] = min(1.0, cache_metadata['predictive_score'][key] + 0.1)
    cache_metadata['priority_score'][key] = calculate_priority_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score with a moderate frequency value, a fresh temporal decay factor, and a predictive score based on the current access context. This ensures new entries are neither immediately evicted nor overly prioritized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] = INITIAL_FREQUENCY
    cache_metadata['temporal_decay'][key] = INITIAL_TEMPORAL_DECAY
    cache_metadata['predictive_score'][key] = INITIAL_PREDICTIVE_SCORE
    cache_metadata['priority_score'][key] = calculate_priority_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive routing model using the data from the evicted entry to refine future access predictions. It also adjusts the temporal decay factors of remaining entries to maintain a balanced priority distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate predictive model (this is a placeholder for actual logic)
    # For simplicity, we just reduce the predictive score slightly for all entries
    for key in cache_snapshot.cache:
        cache_metadata['temporal_decay'][key] *= TEMPORAL_DECAY_FACTOR
        cache_metadata['priority_score'][key] = calculate_priority_score(key)
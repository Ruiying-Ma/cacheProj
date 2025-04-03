# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TEMPORAL_CASCADE = 10
NEUTRAL_HANDOFF_COUNTER = 0
CONTEXTUAL_SYMBIOSIS_FACTOR = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a synergy score for each cache entry, a temporal cascade timestamp, a heuristic handoff counter, and a contextual symbiosis factor that reflects the relationship between cache entries.
temporal_cascade = defaultdict(lambda: INITIAL_TEMPORAL_CASCADE)
handoff_counter = defaultdict(lambda: NEUTRAL_HANDOFF_COUNTER)
contextual_symbiosis = defaultdict(lambda: CONTEXTUAL_SYMBIOSIS_FACTOR)

def calculate_synergy_score(key):
    return (temporal_cascade[key] + handoff_counter[key] + contextual_symbiosis[key])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest synergy score, which is calculated using a combination of the temporal cascade timestamp, heuristic handoff counter, and contextual symbiosis factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_synergy_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_synergy_score(key)
        if score < min_synergy_score:
            min_synergy_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the synergy score of the accessed entry is increased by boosting its temporal cascade timestamp and incrementing its heuristic handoff counter, while also adjusting the contextual symbiosis factor based on the relationship with other entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_cascade[key] += 1
    handoff_counter[key] += 1
    # Adjust contextual symbiosis factor based on some relationship logic
    for other_key in cache_snapshot.cache:
        if other_key != key:
            contextual_symbiosis[other_key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its synergy score with a moderate temporal cascade timestamp, a neutral heuristic handoff counter, and a contextual symbiosis factor that reflects its initial relationship with existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_cascade[key] = INITIAL_TEMPORAL_CASCADE
    handoff_counter[key] = NEUTRAL_HANDOFF_COUNTER
    contextual_symbiosis[key] = CONTEXTUAL_SYMBIOSIS_FACTOR
    # Initialize contextual symbiosis factor based on initial relationship logic
    for other_key in cache_snapshot.cache:
        if other_key != key:
            contextual_symbiosis[other_key] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the synergy scores of remaining entries by adjusting their contextual symbiosis factors to account for the removal of the evicted entry, ensuring the cache adapts to the new context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalibrate contextual symbiosis factors
    for key in cache_snapshot.cache:
        if key != evicted_key:
            contextual_symbiosis[key] -= 1
# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
PREDICTIVE_WEIGHT = 0.2
SYNERGY_BOOST = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic score for each cache entry, which is a composite of access frequency, recency, and a predictive value derived from historical access patterns. It also tracks a synergy index that measures the interdependence of data items based on access sequences.
dynamic_scores = defaultdict(lambda: {'frequency': 0, 'recency': 0, 'predictive': 0})
synergy_index = defaultdict(lambda: defaultdict(float))
access_sequence = deque(maxlen=100)  # Keep track of the last 100 accesses for synergy updates

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest dynamic score, adjusted by the synergy index to preserve data items that are frequently accessed together. This ensures that the cache adapts to changing access patterns while maintaining data synergy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (FREQUENCY_WEIGHT * dynamic_scores[key]['frequency'] +
                 RECENCY_WEIGHT * dynamic_scores[key]['recency'] +
                 PREDICTIVE_WEIGHT * dynamic_scores[key]['predictive'])
        
        # Adjust score by synergy index
        synergy_adjustment = sum(synergy_index[key][other_key] for other_key in cache_snapshot.cache if other_key != key)
        adjusted_score = score - SYNERGY_BOOST * synergy_adjustment
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the dynamic score of the accessed entry by boosting its recency and frequency components. It also updates the synergy index by reinforcing the relationship between the accessed entry and its neighboring entries in recent access sequences.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    dynamic_scores[key]['frequency'] += 1
    dynamic_scores[key]['recency'] = cache_snapshot.access_count
    
    # Update synergy index
    for other_key in access_sequence:
        if other_key != key:
            synergy_index[key][other_key] += 1
            synergy_index[other_key][key] += 1
    
    access_sequence.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its dynamic score based on initial access predictions and updates the synergy index to reflect potential new relationships with existing cache entries. This helps in quickly adapting to new access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    dynamic_scores[key]['frequency'] = 1
    dynamic_scores[key]['recency'] = cache_snapshot.access_count
    dynamic_scores[key]['predictive'] = 0  # Initial predictive value can be zero or based on some heuristic
    
    # Update synergy index with existing cache entries
    for other_key in cache_snapshot.cache:
        if other_key != key:
            synergy_index[key][other_key] = 0
            synergy_index[other_key][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the synergy index to account for the removal of the evicted entry, ensuring that the interdependence of remaining entries is accurately represented. It also adjusts the predictive component of the dynamic scores to better align with current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove evicted entry from synergy index
    if evicted_key in synergy_index:
        del synergy_index[evicted_key]
    for other_key in synergy_index:
        if evicted_key in synergy_index[other_key]:
            del synergy_index[other_key][evicted_key]
    
    # Adjust predictive component of dynamic scores
    for key in dynamic_scores:
        dynamic_scores[key]['predictive'] = max(0, dynamic_scores[key]['predictive'] - 1)
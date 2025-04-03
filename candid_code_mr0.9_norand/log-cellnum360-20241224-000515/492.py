# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_ALIGNMENT_SCORE = 1
INITIAL_EFFICIENCY_SCORE = 1
INITIAL_PREDICTIVE_ADAPTATION_INDEX = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a synchronized trace of access patterns, an alignment score for algorithmic alignment, a usage efficiency score, and a predictive adaptation index for each cache entry.
alignment_scores = defaultdict(lambda: BASELINE_ALIGNMENT_SCORE)
efficiency_scores = defaultdict(lambda: INITIAL_EFFICIENCY_SCORE)
predictive_adaptation_indices = defaultdict(lambda: INITIAL_PREDICTIVE_ADAPTATION_INDEX)
access_patterns = defaultdict(list)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of alignment, efficiency, and predictive adaptation, ensuring that the least promising entry is removed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (alignment_scores[key] + 
                          efficiency_scores[key] + 
                          predictive_adaptation_indices[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the alignment score is incremented to reflect improved algorithmic alignment, the efficiency score is recalculated based on recent access patterns, and the predictive adaptation index is updated to anticipate future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    alignment_scores[key] += 1
    access_patterns[key].append(cache_snapshot.access_count)
    
    # Recalculate efficiency score
    if len(access_patterns[key]) > 1:
        recent_accesses = access_patterns[key][-5:]  # Consider last 5 accesses
        efficiency_scores[key] = len(recent_accesses) / (recent_accesses[-1] - recent_accesses[0] + 1)
    
    # Update predictive adaptation index
    predictive_adaptation_indices[key] = efficiency_scores[key] * alignment_scores[key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the alignment score to a baseline value, sets the efficiency score based on initial access frequency, and calculates an initial predictive adaptation index using synchronized tracing.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    alignment_scores[key] = BASELINE_ALIGNMENT_SCORE
    efficiency_scores[key] = INITIAL_EFFICIENCY_SCORE
    predictive_adaptation_indices[key] = INITIAL_PREDICTIVE_ADAPTATION_INDEX
    access_patterns[key].append(cache_snapshot.access_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the alignment scores of remaining entries to reflect the change in cache dynamics, recalibrates efficiency scores, and updates predictive adaptation indices to account for the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in alignment_scores:
        del alignment_scores[evicted_key]
        del efficiency_scores[evicted_key]
        del predictive_adaptation_indices[evicted_key]
        del access_patterns[evicted_key]
    
    # Adjust scores for remaining entries
    for key in cache_snapshot.cache:
        alignment_scores[key] = max(BASELINE_ALIGNMENT_SCORE, alignment_scores[key] - 1)
        # Recalculate efficiency score
        if len(access_patterns[key]) > 1:
            recent_accesses = access_patterns[key][-5:]  # Consider last 5 accesses
            efficiency_scores[key] = len(recent_accesses) / (recent_accesses[-1] - recent_accesses[0] + 1)
        
        # Update predictive adaptation index
        predictive_adaptation_indices[key] = efficiency_scores[key] * alignment_scores[key]
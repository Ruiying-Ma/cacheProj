# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_THROUGHPUT_SCORE = 1.0
RECENT_ACCESS_BOOST = 0.5
RESOURCE_ISOLATION_THRESHOLD = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including predictive throughput scores for each cache entry, dynamic partitioning boundaries for different resource types, resource isolation levels, and temporal synthesis patterns to track access frequency and recency.
predictive_throughput_scores = defaultdict(lambda: INITIAL_THROUGHPUT_SCORE)
temporal_synthesis_patterns = defaultdict(int)
resource_partitions = defaultdict(list)
resource_isolation_levels = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive throughput score within its partition, while ensuring resource isolation levels are respected. Temporal synthesis patterns are also considered to avoid evicting entries with recent high access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_throughput_scores[key]
        recent_access = temporal_synthesis_patterns[key]
        
        # Check resource isolation level
        if resource_isolation_levels[key] < RESOURCE_ISOLATION_THRESHOLD:
            continue
        
        # Consider temporal synthesis patterns
        if recent_access > 0:
            score += RECENT_ACCESS_BOOST
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive throughput score for the accessed entry is recalculated to reflect its increased utility. The temporal synthesis pattern is updated to mark the recent access, and resource isolation levels are adjusted if necessary to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_throughput_scores[key] += RECENT_ACCESS_BOOST
    temporal_synthesis_patterns[key] = cache_snapshot.access_count
    # Adjust resource isolation levels if necessary
    resource_isolation_levels[key] = min(1.0, resource_isolation_levels[key] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial predictive throughput score based on historical data and current system state. The dynamic partitioning boundaries are adjusted if the new entry affects resource distribution, and temporal synthesis patterns are initialized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_throughput_scores[key] = INITIAL_THROUGHPUT_SCORE
    temporal_synthesis_patterns[key] = cache_snapshot.access_count
    # Initialize resource isolation level
    resource_isolation_levels[key] = 0.5

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive throughput scores of remaining entries to account for the changed cache landscape. Dynamic partitioning boundaries are reassessed, and resource isolation levels are updated to ensure continued balance and efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del predictive_throughput_scores[evicted_key]
    del temporal_synthesis_patterns[evicted_key]
    del resource_isolation_levels[evicted_key]
    
    # Recalibrate scores and resource isolation levels
    for key in cache_snapshot.cache:
        predictive_throughput_scores[key] *= 0.9
        resource_isolation_levels[key] = max(0.0, resource_isolation_levels[key] - 0.1)
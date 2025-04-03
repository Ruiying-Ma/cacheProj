# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LATENCY_WEIGHT = 0.5
TRAJECTORY_WEIGHT = 0.3
RESOURCE_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including adaptive latency scores for each cache entry, a cache trajectory map tracking access patterns, resource harmonization metrics to balance cache resources, and predictive isolation indicators to anticipate future access needs.
adaptive_latency_scores = defaultdict(float)
trajectory_map = defaultdict(list)
resource_harmonization = defaultdict(float)
predictive_isolation = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry based on its adaptive latency, trajectory stability, and resource harmonization. The entry with the lowest score, indicating low future utility and high resource cost, is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        latency_score = adaptive_latency_scores[key]
        trajectory_score = len(trajectory_map[key])
        resource_score = resource_harmonization[key]
        
        composite_score = (LATENCY_WEIGHT * latency_score +
                           TRAJECTORY_WEIGHT * trajectory_score +
                           RESOURCE_WEIGHT * resource_score)
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the adaptive latency score is adjusted based on the current access time, the trajectory map is updated to reflect the new access pattern, resource harmonization metrics are recalibrated to account for the hit, and predictive isolation indicators are refined to better anticipate future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Adjust adaptive latency score
    adaptive_latency_scores[key] = (adaptive_latency_scores[key] + current_time) / 2
    
    # Update trajectory map
    trajectory_map[key].append(current_time)
    
    # Recalibrate resource harmonization
    resource_harmonization[key] += 1
    
    # Refine predictive isolation indicators
    predictive_isolation[key] = len(trajectory_map[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its adaptive latency score based on initial access latency, updates the cache trajectory map to include the new entry, adjusts resource harmonization metrics to accommodate the new entry, and sets initial predictive isolation indicators based on expected access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize adaptive latency score
    adaptive_latency_scores[key] = current_time
    
    # Update trajectory map
    trajectory_map[key] = [current_time]
    
    # Adjust resource harmonization metrics
    resource_harmonization[key] = 1
    
    # Set initial predictive isolation indicators
    predictive_isolation[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates adaptive latency scores for remaining entries, updates the cache trajectory map to remove the evicted entry, adjusts resource harmonization metrics to reflect the freed resources, and refines predictive isolation indicators to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove evicted entry from metadata
    if evicted_key in adaptive_latency_scores:
        del adaptive_latency_scores[evicted_key]
    if evicted_key in trajectory_map:
        del trajectory_map[evicted_key]
    if evicted_key in resource_harmonization:
        del resource_harmonization[evicted_key]
    if evicted_key in predictive_isolation:
        del predictive_isolation[evicted_key]
    
    # Recalibrate adaptive latency scores for remaining entries
    for key in cache_snapshot.cache:
        adaptive_latency_scores[key] *= 0.9  # Decay factor for recalibration
    
    # Adjust resource harmonization metrics
    for key in cache_snapshot.cache:
        resource_harmonization[key] *= 0.9  # Decay factor for recalibration
    
    # Refine predictive isolation indicators
    for key in cache_snapshot.cache:
        predictive_isolation[key] = len(trajectory_map[key])
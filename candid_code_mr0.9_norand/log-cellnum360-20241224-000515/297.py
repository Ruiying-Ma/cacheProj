# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_INDEX_INCREMENT = 1.0
STRATEGIC_COORDINATION_INCREMENT = 1.0
BASELINE_PREDICTIVE_INDEX = 1.0
BASELINE_STRATEGIC_COORDINATION = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Index for each cache entry, which is a score calculated based on historical access patterns and a Resource Allocation Model that dynamically adjusts based on current cache usage and system load. It also tracks a Strategic Coordination score that indicates the importance of each entry in relation to others.
predictive_index = defaultdict(lambda: BASELINE_PREDICTIVE_INDEX)
strategic_coordination = defaultdict(lambda: BASELINE_STRATEGIC_COORDINATION)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of Predictive Index and Strategic Coordination. This ensures that entries with low future access probability and low strategic importance are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = predictive_index[key] + strategic_coordination[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Predictive Index of the accessed entry is increased based on the frequency and recency of access. The Strategic Coordination score is also adjusted to reflect its increased importance in the current workload.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    predictive_index[obj.key] += PREDICTIVE_INDEX_INCREMENT
    strategic_coordination[obj.key] += STRATEGIC_COORDINATION_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Predictive Index based on initial access predictions and assigns a baseline Strategic Coordination score. The Resource Allocation Model is updated to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    predictive_index[obj.key] = BASELINE_PREDICTIVE_INDEX
    strategic_coordination[obj.key] = BASELINE_STRATEGIC_COORDINATION

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the Resource Allocation Model to redistribute resources among remaining entries and adjusts the Strategic Coordination scores to reflect the new cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del predictive_index[evicted_obj.key]
    del strategic_coordination[evicted_obj.key]
    
    # Recalibrate the Resource Allocation Model
    total_size = sum(o.size for o in cache_snapshot.cache.values())
    for key in cache_snapshot.cache:
        strategic_coordination[key] = (cache_snapshot.cache[key].size / total_size) * BASELINE_STRATEGIC_COORDINATION
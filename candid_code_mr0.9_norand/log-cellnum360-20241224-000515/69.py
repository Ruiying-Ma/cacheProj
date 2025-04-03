# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TEMPORAL_SCORE = 1
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5
PREDICTIVE_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue for cache entries, where each entry has a temporal score based on access frequency, recency, and a predictive score derived from historical access patterns. Additionally, it tracks dynamic allocation weights for different types of data to optimize temporal locality.
priority_queue = []
temporal_scores = defaultdict(lambda: INITIAL_TEMPORAL_SCORE)
predictive_scores = defaultdict(float)
access_frequencies = defaultdict(int)
last_access_times = defaultdict(int)
dynamic_allocation_weights = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by choosing the entry with the lowest combined score in the priority queue, considering both the temporal score and the predictive score. This ensures that entries with low likelihood of future access are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        score, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score of the accessed entry is increased based on its recency and frequency of access. The predictive score is adjusted using a lightweight predictive model that updates based on the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequencies[key] += 1
    last_access_times[key] = cache_snapshot.access_count
    temporal_scores[key] = (FREQUENCY_WEIGHT * access_frequencies[key] +
                            RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_times[key]))
    predictive_scores[key] += PREDICTIVE_WEIGHT * (1 / (cache_snapshot.access_count - last_access_times[key] + 1))
    combined_score = temporal_scores[key] + predictive_scores[key]
    heapq.heappush(priority_queue, (combined_score, key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial temporal score based on the object's type and predicted access pattern. The dynamic allocation weights are adjusted to reflect the new distribution of data types in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_scores[key] = INITIAL_TEMPORAL_SCORE
    predictive_scores[key] = 0
    access_frequencies[key] = 1
    last_access_times[key] = cache_snapshot.access_count
    combined_score = temporal_scores[key] + predictive_scores[key]
    heapq.heappush(priority_queue, (combined_score, key))
    # Update dynamic allocation weights
    dynamic_allocation_weights[key] = obj.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority queue by re-evaluating the scores of remaining entries. The dynamic allocation weights are updated to account for the change in cache composition, ensuring optimal space allocation for future entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in temporal_scores:
        del temporal_scores[key]
    if key in predictive_scores:
        del predictive_scores[key]
    if key in access_frequencies:
        del access_frequencies[key]
    if key in last_access_times:
        del last_access_times[key]
    if key in dynamic_allocation_weights:
        del dynamic_allocation_weights[key]
    
    # Rebuild the priority queue
    new_priority_queue = []
    for key in cache_snapshot.cache:
        combined_score = temporal_scores[key] + predictive_scores[key]
        heapq.heappush(new_priority_queue, (combined_score, key))
    priority_queue[:] = new_priority_queue
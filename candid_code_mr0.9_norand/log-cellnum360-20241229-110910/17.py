# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
BASELINE_TEMPORAL_SCORE = 1.0
LOAD_SCORE_FACTOR = 0.1
TEMPORAL_SCORE_INCREMENT = 1.0
ACCESS_INTERVAL_HISTORY_SIZE = 5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including a temporal score based on recent access patterns, a load score reflecting the current system load, and a lightweight history of access intervals to capture temporal locality.
temporal_scores = defaultdict(lambda: BASELINE_TEMPORAL_SCORE)
load_scores = defaultdict(float)
access_intervals = defaultdict(lambda: deque(maxlen=ACCESS_INTERVAL_HISTORY_SIZE))
last_access_time = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each entry, combining the inverse of the temporal score and the load score, prioritizing entries with low temporal locality and high load impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        temporal_score = temporal_scores[key]
        load_score = load_scores[key]
        composite_score = (1 / temporal_score) + load_score
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score of the accessed entry is increased to reflect its recent use, and the access interval history is updated to capture the time since the last access, enhancing the temporal locality profile.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update temporal score
    temporal_scores[key] += TEMPORAL_SCORE_INCREMENT
    
    # Update access interval history
    if last_access_time[key] != 0:
        interval = current_time - last_access_time[key]
        access_intervals[key].append(interval)
    
    # Update last access time
    last_access_time[key] = current_time

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal score to a baseline value, sets its load score based on current system load, and starts its access interval history to track future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize temporal score
    temporal_scores[key] = BASELINE_TEMPORAL_SCORE
    
    # Set load score based on current system load
    load_scores[key] = LOAD_SCORE_FACTOR * (cache_snapshot.size / cache_snapshot.capacity)
    
    # Initialize access interval history
    access_intervals[key] = deque(maxlen=ACCESS_INTERVAL_HISTORY_SIZE)
    
    # Set last access time
    last_access_time[key] = current_time

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the load scores of remaining entries to reflect the reduced load, and recalibrates the temporal scores of similar entries to prevent frequent evictions of similar patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Adjust load scores of remaining entries
    for key in cache_snapshot.cache:
        load_scores[key] = LOAD_SCORE_FACTOR * (cache_snapshot.size / cache_snapshot.capacity)
    
    # Recalibrate temporal scores of similar entries
    for key in cache_snapshot.cache:
        if key != evicted_obj.key:
            temporal_scores[key] = max(BASELINE_TEMPORAL_SCORE, temporal_scores[key] - TEMPORAL_SCORE_INCREMENT)
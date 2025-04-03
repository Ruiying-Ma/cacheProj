# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_FREQUENCY_WEIGHT = 1.0
INITIAL_RECENCY_WEIGHT = 1.0
REAL_TIME_FEEDBACK_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Scalability Index' for each cache entry, which is a composite score derived from an 'Advanced Metric' that combines access frequency, recency, and a real-time feedback loop from system performance metrics. Additionally, a 'Modular Framework' allows for dynamic adjustment of the weight of each component in the Advanced Metric based on workload characteristics.
scalability_index = {}
access_frequency = defaultdict(int)
last_access_time = {}
frequency_weight = INITIAL_FREQUENCY_WEIGHT
recency_weight = INITIAL_RECENCY_WEIGHT
real_time_feedback_weight = REAL_TIME_FEEDBACK_WEIGHT

def calculate_scalability_index(key, current_time):
    frequency_component = access_frequency[key] * frequency_weight
    recency_component = (current_time - last_access_time[key]) * recency_weight
    real_time_feedback_component = real_time_feedback_weight  # Placeholder for real-time feedback
    return frequency_component + recency_component + real_time_feedback_component

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest Scalability Index, ensuring that the least beneficial entry in terms of performance and resource utilization is removed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_index = float('inf')
    for key in cache_snapshot.cache:
        index = calculate_scalability_index(key, cache_snapshot.access_count)
        if index < min_index:
            min_index = index
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the Scalability Index of the accessed entry by boosting its recency and frequency components, while also incorporating real-time feedback to adjust the weight of these components dynamically.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] += 1
    last_access_time[obj.key] = cache_snapshot.access_count
    scalability_index[obj.key] = calculate_scalability_index(obj.key, cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Scalability Index based on initial access patterns and real-time feedback, setting a baseline that can be adjusted as more data is gathered.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = 1
    last_access_time[obj.key] = cache_snapshot.access_count
    scalability_index[obj.key] = calculate_scalability_index(obj.key, cache_snapshot.access_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the weights in the Advanced Metric using the Modular Framework, taking into account the impact of the eviction on system performance to optimize future decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Placeholder for real-time feedback adjustment logic
    # Adjust weights based on system performance metrics
    # For simplicity, let's assume we slightly increase the frequency weight
    global frequency_weight, recency_weight, real_time_feedback_weight
    frequency_weight *= 1.01
    recency_weight *= 0.99
    real_time_feedback_weight *= 1.0  # No change for now
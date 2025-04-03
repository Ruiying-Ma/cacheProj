# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QAS_BASELINE = 1
PE_BASELINE = 0.5
COI_WEIGHTS = {'QAS': 0.4, 'TDT': 0.3, 'PE': 0.3}

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Quantum Adaptation Scores (QAS) for each cache entry, a Temporal Dynamics Tracker (TDT) to monitor access patterns over time, Predictive Entropy (PE) values to estimate future access likelihood, and a Cognitive Optimization Index (COI) to balance between immediate and long-term cache efficiency.
metadata = {
    'QAS': defaultdict(lambda: QAS_BASELINE),
    'TDT': defaultdict(int),
    'PE': defaultdict(lambda: PE_BASELINE),
    'COI': defaultdict(float)
}

def calculate_coi(key):
    return (COI_WEIGHTS['QAS'] * metadata['QAS'][key] +
            COI_WEIGHTS['TDT'] * metadata['TDT'][key] +
            COI_WEIGHTS['PE'] * metadata['PE'][key])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest Cognitive Optimization Index (COI), which is calculated using a weighted combination of the Quantum Adaptation Score (QAS), Temporal Dynamics Tracker (TDT), and Predictive Entropy (PE).
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_coi = float('inf')
    
    for key in cache_snapshot.cache:
        coi = calculate_coi(key)
        if coi < min_coi:
            min_coi = coi
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Adaptation Score (QAS) is incremented to reflect increased relevance, the Temporal Dynamics Tracker (TDT) is updated to capture the latest access time, and the Predictive Entropy (PE) is recalculated to adjust future access predictions. The Cognitive Optimization Index (COI) is then recalculated based on these updated values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['QAS'][key] += 1
    metadata['TDT'][key] = cache_snapshot.access_count
    # Recalculate PE based on some heuristic, here we just increment for simplicity
    metadata['PE'][key] += 0.1
    metadata['COI'][key] = calculate_coi(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Adaptation Score (QAS) is initialized to a baseline value, the Temporal Dynamics Tracker (TDT) is set to the current time, and the Predictive Entropy (PE) is estimated based on initial access patterns. The Cognitive Optimization Index (COI) is computed to integrate these initial metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['QAS'][key] = QAS_BASELINE
    metadata['TDT'][key] = cache_snapshot.access_count
    metadata['PE'][key] = PE_BASELINE
    metadata['COI'][key] = calculate_coi(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Predictive Entropy (PE) of remaining entries to account for the change in cache composition, and adjusts the Cognitive Optimization Index (COI) of all entries to ensure optimal balance between immediate and long-term cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        # Recalibrate PE based on some heuristic, here we just decrement for simplicity
        metadata['PE'][key] -= 0.05
        metadata['COI'][key] = calculate_coi(key)
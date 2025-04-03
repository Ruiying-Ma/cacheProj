# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_QSL = 1
MODERATE_ECS = 5
TRT_INCREMENT = 1
ECS_DECREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Synchronization Loop (QSL) counter for each cache entry, an Entropic Cycle Shift (ECS) value representing the entry's entropy level, a Temporal Resonance Tracker (TRT) to monitor access patterns over time, and a Heuristic Integration Mechanism (HIM) score that combines these factors to assess the entry's overall importance.
QSL = defaultdict(int)
ECS = defaultdict(int)
TRT = defaultdict(int)
HIM = defaultdict(int)

def calculate_him(key):
    return QSL[key] + ECS[key] + TRT[key]

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest HIM score, which is calculated by integrating the QSL, ECS, and TRT values. This approach ensures that entries with low temporal resonance, high entropy, and low synchronization are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_him_score = float('inf')
    
    for key in cache_snapshot.cache:
        him_score = calculate_him(key)
        if him_score < min_him_score:
            min_him_score = him_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QSL counter for the accessed entry is incremented, the ECS value is adjusted to reflect reduced entropy, and the TRT is updated to enhance the entry's temporal resonance. The HIM score is recalculated to reflect these changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QSL[key] += 1
    ECS[key] = max(0, ECS[key] - ECS_DECREMENT)
    TRT[key] += TRT_INCREMENT
    HIM[key] = calculate_him(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QSL counter is initialized to a base value, the ECS is set to a moderate level to indicate initial uncertainty, and the TRT is initialized to track future access patterns. The HIM score is computed based on these initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QSL[key] = BASE_QSL
    ECS[key] = MODERATE_ECS
    TRT[key] = 0
    HIM[key] = calculate_him(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the ECS values of remaining entries to account for the reduced cache entropy, adjusts the TRT to reflect the new temporal dynamics, and recalculates the HIM scores to ensure accurate future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        ECS[key] = max(0, ECS[key] - ECS_DECREMENT)
        TRT[key] = max(0, TRT[key] - TRT_INCREMENT)
        HIM[key] = calculate_him(key)
# Import anything you need below
import math

# Put tunable constant parameters below
BASELINE_QVI = 1
QVI_INCREMENT = 1
DFC_QVI_WEIGHT_INCREMENT = 0.01
DFC_NSM_WEIGHT_INCREMENT = 0.01

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Variability Index (QVI) for each cache entry, a Predictive Entropic Flow (PEF) score for the overall cache, a Neural Stability Matrix (NSM) that tracks the stability of access patterns, and a Dynamic Fusion Calibration (DFC) factor that adjusts the weight of each component dynamically.
QVI = {}
PEF = 0
NSM = {}
DFC = {'QVI': 1.0, 'PEF': 1.0, 'NSM': 1.0}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry using QVI, PEF, and NSM, weighted by the DFC. The entry with the lowest composite score is selected for eviction, ensuring a balance between recent access patterns and predicted future utility.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        qvi_score = QVI.get(key, BASELINE_QVI)
        nsm_score = NSM.get(key, 0)
        composite_score = (DFC['QVI'] * qvi_score) + (DFC['PEF'] * PEF) + (DFC['NSM'] * nsm_score)
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QVI of the accessed entry is incremented to reflect its recent use, the PEF is recalibrated to account for the change in access entropy, and the NSM is updated to reinforce the stability of the current access pattern. The DFC is adjusted to slightly increase the weight of QVI in future decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Increment QVI for the accessed object
    QVI[obj.key] = QVI.get(obj.key, BASELINE_QVI) + QVI_INCREMENT
    
    # Recalibrate PEF (simplified as a function of cache size and access count)
    PEF = math.log(cache_snapshot.size + 1) / (cache_snapshot.access_count + 1)
    
    # Update NSM for the accessed object
    NSM[obj.key] = NSM.get(obj.key, 0) + 1
    
    # Adjust DFC to increase weight of QVI
    DFC['QVI'] += DFC_QVI_WEIGHT_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QVI is initialized to a baseline value, the PEF is updated to reflect the new entropy state of the cache, and the NSM is adjusted to incorporate the new access pattern. The DFC is recalibrated to ensure balanced consideration of all metadata components.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize QVI for the new object
    QVI[obj.key] = BASELINE_QVI
    
    # Update PEF
    PEF = math.log(cache_snapshot.size + 1) / (cache_snapshot.access_count + 1)
    
    # Adjust NSM for the new object
    NSM[obj.key] = 1
    
    # Recalibrate DFC
    total_weight = DFC['QVI'] + DFC['PEF'] + DFC['NSM']
    DFC['QVI'] = DFC['PEF'] = DFC['NSM'] = 1.0 / total_weight

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the PEF is recalculated to account for the reduced entropy, the NSM is updated to remove the influence of the evicted entry, and the DFC is adjusted to slightly increase the weight of NSM in future decisions, promoting stability in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalculate PEF
    PEF = math.log(cache_snapshot.size + 1) / (cache_snapshot.access_count + 1)
    
    # Update NSM to remove influence of evicted entry
    if evicted_obj.key in NSM:
        del NSM[evicted_obj.key]
    
    # Adjust DFC to increase weight of NSM
    DFC['NSM'] += DFC_NSM_WEIGHT_INCREMENT
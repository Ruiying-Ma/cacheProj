# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
TRAJECTORY_LENGTH = 10  # Length of the trajectory vector
ENTROPY_WEIGHT = 0.5    # Weight for entropy in eviction decision
CONSISTENCY_WEIGHT = 0.5 # Weight for consistency in eviction decision

# Put the metadata specifically maintained by the policy below. The policy maintains a trajectory vector for each cache entry, representing its access pattern over time. It also tracks a synchronization vector to align these trajectories with a global access pattern. Additionally, it uses an entropy map to measure the randomness of access patterns and a consistency score to evaluate the stability of these patterns.
trajectory_vectors = defaultdict(lambda: np.zeros(TRAJECTORY_LENGTH))
synchronization_vectors = defaultdict(lambda: np.zeros(TRAJECTORY_LENGTH))
entropy_map = defaultdict(float)
consistency_scores = defaultdict(float)
global_sync_vector = np.zeros(TRAJECTORY_LENGTH)

def calculate_entropy(vector):
    # Calculate entropy as a measure of randomness
    probabilities = vector / np.sum(vector) if np.sum(vector) > 0 else vector
    return -np.sum(probabilities * np.log2(probabilities + 1e-9))

def calculate_consistency(vector):
    # Calculate consistency as a measure of stability
    return np.std(vector)

def evict(cache_snapshot, obj):
    candid_obj_key = None
    max_score = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        trajectory = trajectory_vectors[key]
        sync_vector = synchronization_vectors[key]
        
        entropy = entropy_map[key]
        consistency = consistency_scores[key]
        
        deviation = np.linalg.norm(trajectory - global_sync_vector)
        
        score = (ENTROPY_WEIGHT * entropy) - (CONSISTENCY_WEIGHT * consistency) + deviation
        
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    key = obj.key
    trajectory = trajectory_vectors[key]
    
    # Update trajectory vector
    trajectory = np.roll(trajectory, -1)
    trajectory[-1] = cache_snapshot.access_count
    
    # Update synchronization vector
    sync_vector = synchronization_vectors[key]
    sync_vector = (sync_vector + trajectory) / 2
    
    # Recalculate entropy and consistency
    entropy_map[key] = calculate_entropy(trajectory)
    consistency_scores[key] = calculate_consistency(trajectory)
    
    # Update global synchronization vector
    global_sync_vector[:] = np.mean(list(synchronization_vectors.values()), axis=0)

def update_after_insert(cache_snapshot, obj):
    key = obj.key
    trajectory = trajectory_vectors[key]
    
    # Initialize trajectory vector
    trajectory[:] = np.linspace(0, cache_snapshot.access_count, TRAJECTORY_LENGTH)
    
    # Set synchronization vector
    synchronization_vectors[key] = global_sync_vector.copy()
    
    # Update entropy and consistency
    entropy_map[key] = calculate_entropy(trajectory)
    consistency_scores[key] = calculate_consistency(trajectory)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    evicted_key = evicted_obj.key
    
    # Remove evicted entry from metadata
    del trajectory_vectors[evicted_key]
    del synchronization_vectors[evicted_key]
    del entropy_map[evicted_key]
    del consistency_scores[evicted_key]
    
    # Recalibrate global synchronization vector
    if synchronization_vectors:
        global_sync_vector[:] = np.mean(list(synchronization_vectors.values()), axis=0)
    else:
        global_sync_vector[:] = np.zeros(TRAJECTORY_LENGTH)
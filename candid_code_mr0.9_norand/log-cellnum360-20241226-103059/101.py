# Import anything you need below
import numpy as np

# Put tunable constant parameters below
TRANSPOSE_INTERVAL = 100  # Number of accesses after which to transpose the matrix

# Put the metadata specifically maintained by the policy below. The policy maintains a matrix where each row represents a cache line and each column represents a specific metadata attribute such as access frequency, recency, and a scaling factor. The matrix is transposed periodically to optimize access patterns and reduce complexity.
metadata_matrix = {}  # Dictionary to hold metadata for each object key
access_counter = 0  # Counter to track accesses for transposing

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the row in the transposed matrix with the lowest combined score of access frequency and recency, adjusted by the scaling factor. This allows for a balanced decision that considers both recent usage and overall access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, (freq, recency, scale) in metadata_matrix.items():
        score = (freq + recency) * scale
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the corresponding row in the matrix by incrementing the access frequency and adjusting the recency value. The scaling factor is recalculated to reflect the current access pattern, ensuring that frequently accessed items are prioritized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    global access_counter
    access_counter += 1
    if obj.key in metadata_matrix:
        freq, recency, scale = metadata_matrix[obj.key]
        freq += 1
        recency = cache_snapshot.access_count
        scale = 1 / (1 + freq)  # Example scaling factor
        metadata_matrix[obj.key] = (freq, recency, scale)
    
    if access_counter >= TRANSPOSE_INTERVAL:
        transpose_matrix()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds a new row to the matrix with initial values for access frequency and recency. The scaling factor is initialized based on the current state of the cache to ensure balanced scaling across all entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    freq = 1
    recency = cache_snapshot.access_count
    scale = 1 / (1 + freq)  # Example scaling factor
    metadata_matrix[obj.key] = (freq, recency, scale)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the corresponding row from the matrix and recalculates the scaling factors for the remaining entries. This ensures that the matrix remains optimized for parallel execution and complexity reduction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in metadata_matrix:
        del metadata_matrix[evicted_obj.key]
    
    # Recalculate scaling factors for remaining entries
    for key in metadata_matrix:
        freq, recency, _ = metadata_matrix[key]
        scale = 1 / (1 + freq)  # Example scaling factor
        metadata_matrix[key] = (freq, recency, scale)

def transpose_matrix():
    '''
    This function transposes the metadata matrix to optimize access patterns and reduce complexity.
    - Return: `None`
    '''
    global access_counter
    # Transpose logic can be implemented here if needed
    access_counter = 0  # Reset access counter after transposing
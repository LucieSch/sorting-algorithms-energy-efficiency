def generate_random_int_array(n, max_val=1000000, seed=None):
    import random
    if seed is not None:
        random.seed(seed)
    
    return [random.randint(0, max_val) for _ in range(n)]

def generate_almost_sorted_int_array(sorted_arr):
    import random
    arr = sorted_arr.copy()
    n = len(arr)

    # Swap 1 % of the elements to create an almost sorted array
    for _ in range(n // 100):
        i = random.randint(0, n-1)
        j = random.randint(0, n-1)
        arr[i], arr[j] = arr[j], arr[i]

    return arr

def generate_all_int_inputs(n, max_val=1000000, seed=None):
    base = generate_random_int_array(n, max_val, seed)

    unsorted_int_array = base.copy()
    sorted_int_array = sorted(base)
    reverse_sorted_int_array = sorted(base, reverse=True)
    almost_sorted_int_array = generate_almost_sorted_int_array(sorted_int_array)

    return unsorted_int_array, sorted_int_array, reverse_sorted_int_array, almost_sorted_int_array
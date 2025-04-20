def safe_neighbor_check(x, y, size, action, extra_predicate=lambda x, y: True):
    """given an x, y and size contraint (and optionally an additional predicate),
    will safely iterate through all the neighbors and if the neighbor is in the range in both x and y AND meets the extra predicate,
    then it will run action, inputting x and y"""
    return_values = []
    if x+1 < size and extra_predicate(x+1, y):
        return_values.append(action(x+1,y))
    if x-1 >= 0 and extra_predicate(x-1,y):
        return_values.append(action(x-1,y))
    if y+1 < size and extra_predicate(x,y+1):
        return_values.append(action(x,y+1))
    if y-1 >= 0 and extra_predicate(x,y-1):
        return_values.append(action(x,y-1))
    return return_values
    



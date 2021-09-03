# check if the candidates are alL None
def checkNone(c_can):
    for key, value in c_can.items():
        if value != None:
            return False
    return True

# Move the iterator to the pivot required document ID position
def seekToDocument(sorted_can_list, cur_can, t, iterator, pivot):
    flag = 0
    term_index = sorted_can_list[t][0]
    target_doc = cur_can[pivot][0]
    while flag == 0 :
        item = next(iterator[term_index], None)
        if item == None:
            flag = 1
            cur_can[term_index] = item
        elif item[0] >= target_doc:
            cur_can[term_index] = item
            flag = 1
        
# Sort a dictionary with None value and put the None value to the back of the
# dictionary 
def sortDict(a):
        minval = 9999;
        keys = []
        for key, val in a.items():
            if val is None:
                a[key] = (minval,minval)
                keys.append(key)

        li = sorted(a.items(), key=lambda e:e[1][0])

        for i in range(len(li)):
            if li[i][1][0] == minval:
                li[i] = None
        
        for key, val in a.items():
            if val == (minval, minval):
                a[key] = None
        return li

# Get the document ID of position 't' in candidates dictionary
def getDocID(cur_can, t):
    while t < len(cur_can)-1 and cur_can[t] == None:
        t = t + 1
    if t >= len(cur_can):
        return -1000
    elif cur_can[t] == None:
        return -1000
    return cur_can[t][1][0]
    

def WAND_Algo(query_terms, top_k, inverted_index):
    # Initializing
    fully_scored = 0
    U = {}
    iterator = {}
    
    # Initializing Upper Bound Dictionary and Iterator dictionary
    for t in range(len(query_terms)):
        U[t] = max((inverted_index[query_terms[t]]), key = lambda i: i[1])[1]
        iterator[t] = iter(inverted_index[query_terms[t]])
    
    ult_upper = 0
    for i in range(len(U)):
        ult_upper = ult_upper + U[i]
    
    # Initialize all first posting document to cur_can
    cur_can = {}
    for j in range(len(query_terms)):
        cur_can[j] = next(iterator[j], None)

    theta = -10
    Ans = []
    fla = 0
    tem_s_lim = 0
    while checkNone(cur_can) != True:
        # sort the candidates according to the document ID
        sorted_can_list = sortDict(cur_can)
        # print(sorted_can_list)
        score_limit = 0
        r_pivot = 0
        if len(query_terms) == 1:
            tem_s_lim = score_limit + U[sorted_can_list[r_pivot][0]]
            score_limit = tem_s_lim
        else:
            while r_pivot < len(query_terms)-1:
                if sorted_can_list[r_pivot] != None:
                    tem_s_lim = score_limit + U[sorted_can_list[r_pivot][0]]
                    if tem_s_lim > theta:
                        break
                    
                    score_limit = tem_s_lim
                    r_pivot = r_pivot + 1
                # If the pivot choosed is already None then terminate the LOOP
                # by changing the 'fla' parameter
                else:
                    fla = 1
                    break
                
        if fla == 1:
            break
        
        # set pivot to the real index when it is initialized in query term string
        if sorted_can_list[r_pivot] != None:
            pivot = sorted_can_list[r_pivot][0]
            for item in sorted_can_list:
                if item == None:
                    break
                elif item[0] == pivot:
                    n = item[1][0]
                    break
        else:
            break


        if getDocID(sorted_can_list, 0) == n:
            s = 0
            t = 0
            fully_scored = fully_scored+1
            while (t < len(query_terms)) and (getDocID(sorted_can_list, t) == n):
                s = s + sorted_can_list[t][1][1]
                true_index = sorted_can_list[t][0]
                cur_can[true_index] = next(iterator[true_index], None)
                
                t = t + 1
     
            if s > theta:
                for i in sorted_can_list:
                    if i[0] == pivot:
                        Ans.append((s, i[1][0]))
                        break
                
                if len(Ans) > top_k:
                    Ans.sort(key = lambda i: i[0], reverse = True)
                    Ans.pop(len(Ans)-1)
                    theta = Ans[len(Ans)-1][0]
                
        else:
            t = 0
            # Handle the situation where the r_pivot == 1, then while t < r_pivot-1
            # will not excute seekToDocument
            if r_pivot == 1:
                seekToDocument(sorted_can_list, cur_can, 0, iterator, pivot)
            else:
                while t < r_pivot-1:
                    seekToDocument(sorted_can_list, cur_can, t, iterator, pivot)
                    t = t+1
                    
        if len(Ans) == top_k and Ans[top_k - 1][0] == ult_upper and theta > 0:
            break                             
    return Ans , fully_scored

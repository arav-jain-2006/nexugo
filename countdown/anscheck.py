answers= []
#x={}
def printList(list,target):
    x= {}
    a= 0
    x.clear()
    for (num, sign) in list:    
        oof= f"{sign}{num}" 
        a= oof 
        x[a]= (f"{sign}{num}")
    #print()
    eq=''
    for i in x:
        eq= eq+str(i)
        #print(eq)
        try:
          ans= (eval(eq))
          if ans==target:
             answers.append(eq)
             #print(x)
        except:
             pass
    return
 
# Print all ways to calculate a target from elements of specified list
def printWays(A, n, target, sum=0,list=[]):

    # base case: if target is found, print result list
    if sum == target:
        printList(list,target)
        return

    # base case: No elements are left
    if n < 0:
        return

    # Ignores the current element
    printWays(A, n - 1, target, sum, list)

    # Consider the current element and subtract it from the target
    list.append((A[n], '+'))
    printWays(A, n - 1, target, sum + A[n], list)
    list.pop()  # backtrack
    
    list.append((A[n], '/'))
    printWays(A, n - 1, target, sum / A[n], list)
    list.pop()  # backtrack
    
    list.append((A[n], '*'))
    printWays(A, n - 1, target, sum * A[n], list)
    list.pop()  # backtrack

    # Consider the current element and add it to the target
    list.append((A[n], '-'))
    printWays(A, n - 1, target, sum - A[n], list)
    list.pop()  # backtrack


def posAns(nums,target):
    realnums=[]
    for num in nums:
        realnums.append(int(num))
    printWays(realnums,len(realnums)-1,target)
    global answers
    answers= (list(set(answers)))
    realnums.clear()
    realans=[]
    realans.clear()
    for ans in answers:
       eq=(ans[1:])
       if eval(eq)==target:
          eq= eq.replace('*','x')
          realans.append(eq)
    answers.clear()
    #x.clear()
    #print(x)
    #print(answers)
    #print(realans)
    if realans!=[]:
     return (realans)
    else:
        return 'Invalid'
# input list and target number
'''
print(anscheck([50,25,3,6,2,5],2500))
print(anscheck([100,20,30,30,20,10],2000))
print(anscheck([299,9929,92929,9929,93848,83838],9929))
'''
#print(anscheck([1,2,3,1,4,5],55))


basket = [1,2,3,4,5,3]

def findDuplicate(fruits:list[str]):
    tortoise = fruits[0]#1
    hare = fruits[0]#1
    
    while True:
        print('tortoise position: ',tortoise,'hare position: ',hare)
        tortoise= fruits[tortoise]
        hare= fruits[fruits[hare]]
        if tortoise== hare:
            break
    
    print('tortoise position: ',tortoise,'hare position: ',hare)
    pointer1 = fruits[0]#1
    pointer2 = tortoise #4
    print('pointer1: ',pointer1,'pointer2: ',pointer2)

    while pointer1 != pointer2:
        pointer1 = fruits[pointer1]#3
        pointer2 = fruits[pointer2]#5
        print('pointer1: ',pointer1,'pointer2: ',pointer2)
    return pointer1

findDuplicate(basket)
# Python: no LinkedList module, so use your own
from linking_nodes import LinkedList,printList

def removeDups(uLL):
    """uLL: head is node with key,next attributes

    Retrun a new linked list, don't modify uLL
    """
    curr= uLL.head
    d= set([uLL.head.val])
    while curr.next: 
        if curr.next.val in d:
            curr.next = curr.next.next
        else:
            d.add(curr.next.val)
            curr= curr.next

def removeDupsNoBuff(uLL):
    """modify uLL to have its dups removed"""
    curr= uLL.head
    #d= set([uLL.head.val])
    while curr.next: 
        ptr= curr
        while ptr.next:
            if ptr.next.val == curr.val:
                ptr.next= ptr.next.next
            else:
                ptr= ptr.next
        curr= curr.next

if __name__ == "__main__":
    LL= LinkedList()
    for key in 'kaylan':
        LL.insert(key)
    printList(LL.head)
    print('removeDups')
    removeDups(LL)
    printList(LL.head)

    LL= LinkedList()
    for key in 'kaylan':
        LL.insert(key)
    printList(LL.head)
    print('removeDupsNoBuff')
    removeDupsNoBuff(LL)
    printList(LL.head)


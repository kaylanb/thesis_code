import unittest

from collections import deque

class Node(object):
    """
    Attributes:
        val: 
        next:
    """
    def __init__(self,val=None):
        self.val= val
        self.next= None

class LinkedList(object):
    """
    Attributes:
        head
    """
    def __init__(self):
        self.head= None

    def insert(self,data):
        node= Node(data)
        node.next= self.head
        self.head= node

    def remove(self,data):
        """delete the Node that has Node.data == data"""
        curr= self.head
        prev= None
        found=False
        while (curr) and (not found):
            if curr.val == data:
                found=True
            else:
                prev=curr
                curr= curr.next
        if not found:
            print('WARNING, nothing to remove with val = ',data)
        elif prev:
            prev.next= curr.next
        else:
            self.head= curr.next  

    def isEmpty(self):
        return not self.head      


def printList(node):
    while(node):
        print(node.val)
        node= node.next

# WARNING: Python list is O(n) for pop() and insert()!
class Stack(object):
    def __init__(self):
        self.things=deque()

    def pop(self):
        return self.things.pop()

    def push(self,data):
        self.things.append(data)

    def peek(self):
        return self.things[-1]
    
    def isEmpty(self):
        return len(self.things) == 0

    def size(self):
        return len(self.things)

class Queue(object):
    def __init__(self):
        self.things= deque()

    def pop(self):
        return self.things.pop()

    def push(self,data):
        self.things.appendleft(data)

    def peek(self):
        return self.things[-1]

    def isEmpty(self):
        return len(self.things) == 0

    def size(self):
        return len(self.things)


class TestLinkedList(unittest.TestCase):
    def setUp(self):
        self.data= [10,5,-1]

    def test_insert_remove(self):
        ll= LinkedList()
        for d in self.data:
            ll.insert(d)
            self.assertEqual(ll.head.val, d)
        for d in self.data:
            self.assertEqual(ll.remove(d),d)
        self.assertTrue(ll.next() is None)

class TestStack(unittest.TestCase):
    def setUp(self):
        self.data= [10,5,-1]

    def test_push_pop(self):
        s=Stack()
        for d in self.data:
            s.push(d)
            self.assertEqual(s.peek(), d)
        for d in self.data[::-1]:
            self.assertEqual(s.pop(), d)
        self.assertTrue(s.isEmpty())

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.data= [10,5,-1]

    def test_add_remove(self):
        q= Queue()
        for d in self.data:
            q.push(d)
            self.assertEqual(q.peek(), self.data[0])
        for d in self.data:
            self.assertEqual(q.pop(), d)
        self.assertTrue(q.isEmpty())


if __name__ == "__main__":
    unittest.main()
    # data= [10,5,-1]
    # ll= LinkedList()
    # for d in data:
    #     ll.insert(d)
    # printList(ll.head)
    # for d in data:
    #     ll.remove(d)
    #     print('removed',d,'list=')
    #     printList(ll.head)
    # assert(ll.isEmpty())
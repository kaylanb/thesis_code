import unittest

class Node(object):
    """
    Attributes:
        data: 
        next:
    """
    def __init__(self,data=None,next=None):
        self.data= data
        self.next= next

class LinkedList(object):
    """
    Attributes:
        head
    """

    def __init__(self):
        self.head=None

    def insert(self,data):
        new_node= Node(data)
        new_node.next= self.head
        self.head= new_node

    def remove(self,data):
        """delete the Node that has Node.data == data"""
        curr_node= self.head
        prev_node= None
        while(curr_node):
            if curr_node.data == data:
                # Skip the node we are deleting
                if prev_node:
                    prev_node.next= curr_node.next
                else:
                    self.head= curr_node.next
                return
            prev_node= curr_node
            curr_node= curr_node.next
        raise ValueError("Node not found")

class Stack(object):
    """
    Attributes:
        pop
        push
        peek
        isEmpty
    """
    def __init__(self):
        self.top= None
        self.size= 0

    def push(self,data):
        new_node= Node(data,next=self.top)
        self.top= new_node
        self.size += 1

    def pop(self):
        the_top_val= self.top.data
        self.top= self.top.next
        self.size -= 1
        return the_top_val

    def peek(self):
        return self.top

    def isEmpty(self):
        return self.size == 0


class Queue(object):
    """
    Attributes:
        remove
        add
        peek
        isEmpty
    """
    def __init__(self):
        self.ll = LinkedList()
        self.first= None
        self.last= None
        self.size= 0

    def add(self,data):
        self.ll.insert(data)
        self.last= self.ll.head
        self.size +=1
        if self.size == 1:
            self.first= self.last
            self.first.next= None
        if self.size == 2:
            self.first.next= self.last

    # def add(self,data):
    #     self.last= Node(data,next=self.last)
    #     self.size +=1
    #     if self.size == 1:
    #         self.first= self.last
    #     if self.size == 2:
    #         self.first.next= self.last

    def remove(self):
        data= self.first.data
        self.first= self.first.next
        self.size -= 1
        return data

    def peek(self):
        return self.first
    
    def isEmpty(self):
        return self.size == 0

class TestLinkedList(unittest.TestCase):
    def setUp(self):
        data= [10,5,-1]
        self.ll= LinkedList()
        for d in data:
            self.ll.insert(Node(d))

    def test_insert(self):
        self.assertEqual(self.ll.head.data, -1)
        self.assertEqual(self.ll.head.next.data, 5)

    def test_remove(self):
        self.ll.remove(5)
        self.assertEqual(self.ll.head.data, -1)
        self.assertEqual(self.ll.head.next.data, 10)
        self.ll.remove(-1)
        self.assertEqual(self.ll.head.data, 10)

class TestStack(unittest.TestCase):
    def setUp(self):
        data= [10,5,-1]
        self.stack= Stack()
        for d in data:
            self.stack.push(d)

    def test_push(self):
        self.assertEqual(self.stack.peek().data, -1)
        self.assertEqual(self.stack.peek().next.data, 5)
        self.assertEqual(self.stack.peek().next.next.data, 10)

    def test_pop(self):
        d =self.stack.pop()
        self.assertEqual(d, -1)
        self.assertEqual(self.stack.peek().data, 5)
        d= self.stack.pop()
        self.assertEqual(d, 5)
        self.assertEqual(self.stack.peek().data, 10)

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.data= [10,5,-1]
        self.ds= Queue()
        #for d in data:

    def test_add_one(self):
        self.ds.add(self.data[0])
        self.assertEqual(self.ds.first.data, 10)
        self.assertEqual(self.ds.first.next, None)
        self.assertEqual(self.ds.last.data, 10)
        self.assertEqual(self.ds.last.next, None)

    def test_add_two(self):
        self.ds.add(self.data[0])
        self.ds.add(self.data[1])
        self.assertEqual(self.ds.first.data, 10)
        self.assertEqual(self.ds.first.next.data, 5)

    def test_remove(self):
        for d in self.data:
            self.ds.add(d)
        print('DATA')
        print(self.ds.first.data)
        print(self.ds.first.next.data)
        print(self.ds.first.next.next.data)
        print(self.ds.first.next.next.next.data)
        d= self.ds.remove()
        self.assertEqual(d, 10)
        self.assertEqual(self.ds.peek().data, 5)
        d= self.ds.remove()
        self.assertEqual(d, 5)
        self.assertEqual(self.ds.peek().data, -1)


    # def test_remove(self):
    #     d =self.ds.remove()
    #     self.assertEqual(d, 10)
    #     self.assertEqual(self.ds.peek().data, 5)
    #     d= self.ds.remove()
    #     self.assertEqual(d, 5)
    #     self.assertEqual(self.ds.peek().data, -1)


if __name__ == "__main__":
    unittest.main()
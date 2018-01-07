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

    def insert(self,Node):
        Node.next= self.head
        self.head= Node

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

class TestLinkedList(unittest.TestCase):
    def setUp(self):
        data= [10,5,-1]
        self.ll= LinkedList()
        for d in data:
            self.ll.insert(Node(d))

    # def tearDown(self):
    #     self.ll.dispose()
    #     self.ll = None


    def test_insert(self):
        self.assertEqual(self.ll.head.data, -1)
        self.assertEqual(self.ll.head.next.data, 5)

    def test_remove(self):
        self.ll.remove(5)
        self.assertEqual(self.ll.head.data, -1)
        self.assertEqual(self.ll.head.next.data, 10)
        self.ll.remove(-1)
        self.assertEqual(self.ll.head.data, 10)


if __name__ == "__main__":
    unittest.main()
import unittest

import heapq
from collections import deque
from linking_nodes import Queue

class BinaryTree(object):
    def __init__(self,key=None,lc=None,rc=None):
        self.key= key
        self.leftChild= lc
        self.rightChild= rc

    def insertLeft(self,key):
        node= BinaryTree(key)
        if self.leftChild:
            tmp= self.leftChild
            self.leftChild= node
            node.leftChild= tmp
        else:
            self.leftChild= node

    def insertRight(self,key):
        node= BinaryTree(key)
        if self.rightChild:
            tmp= self.rightChild
            self.rightChild= node
            node.rightChild= tmp
        else:
            self.rightChild= node

def visit(node):
    print(node.key)

def tree_traverse(node,how='in',visit_func=visit):
    """how: in,pre,post"""
    if node:
        if how == 'pre':
            visit_func(node)
            tree_traverse(node.leftChild,how=how,
                          visit_func=visit_func)
            tree_traverse(node.rightChild,how=how,
                          visit_func=visit_func)
        elif how == 'post':
            tree_traverse(node.leftChild,how=how,
                          visit_func=visit_func)
            tree_traverse(node.rightChild,how=how,
                          visit_func=visit_func)
            visit_func(node)
        elif how == 'in':
            tree_traverse(node.leftChild,how=how,
                          visit_func=visit_func)
            visit_func(node)
            tree_traverse(node.rightChild,how=how,
                          visit_func=visit_func)

class bstNode(BinaryTree):
    def __init__(self,key=None,lc=None,rc=None,
                 parent=None,val2store=None):
        super().__init__(key,lc,rc)
        self.parent= parent
        self.val2store= val2store

    def isLeftChild(self):
        return self == self.parent.leftChild

    def isRightChild(self):
        return self == self.parent.rightChild

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return (not self.leftChild) and (not self.rightChild)

    def overwrite_with(self,node):
        for attr in ['key','leftChild','rightChild',
                     'val2store','parent']:
            setattr(self,attr, getattr(node,attr))

    def hasBothChildren(self):
        return self.leftChild and self.rightChild


class BST(object):
    def __init__(self):
        self.root= None

    def insert(self,key,val2store):
        if not self.root:
            self.root= bstNode(key=key,val2store=val2store)
        else:
            self._insert(key,val2store,self.root)

    def _insert(self,key,val2store,root):
        if key < root.key:
            if root.leftChild:
                self._insert(key,val2store,root.leftChild)
            else:
                root.leftChild= bstNode(key=key,val2store=val2store,
                                        parent=root)
        else:
            if root.rightChild:
                self._insert(key,val2store,root.rightChild)
            else:
                root.rightChild= bstNode(key=key,val2store=val2store,
                                         parent=root)

    def get(self,key):
        """return the val2store"""
        if not self.root:
            return None
        else:
            return self._get(key,self.root).val2store

    def _get(self,key,root):
        """Recursion, return the node"""
        if not root:
            return None
        elif root.key == key:
            return root
        elif key < root.key:
            return self._get(key,root.leftChild)
        else:
            return self._get(key,root.rightChild)

    def getSmallest(self,node):
        min_node= node
        for new_node in tree:
            if new_node.key < min_node.key:
                min_node= new_node
        return min_node

    def delete(self,key):
        """Set references to this node to None"""
        delnode= self._get(key,self.root)
        print('left,right',delnode.leftChild,delnode.rightChild)
        if not delnode:
            raise KeyError('key=%s not in tree, cannot delete' % key)
        if delnode.isLeaf():
            if delnode.isLeftChild():
                delnode.parent.leftChild= None
            else:
                delnode.parent.rightChild= None
        elif delnode.hasBothChildren():
            raise ValueError("delnode has 2 children, couldn't figure out code to delte this type of node")
        else:
            # One child
            if delnode.isRoot():
                if delnode.leftChild:
                    delnode.overwrite_with(delnode.leftChild)
                else:
                    delnode.overwrite_with(delnode.rightChild)
            elif delnode.isLeftChild():
                if delnode.leftChild:
                    delnode.parent.leftChild= delnode.leftChild
                    delnode.leftChild.parent= delnode.parent 
                else:
                    delnode.parent.leftChild= delnode.rightChild
                    delnode.rightChild.parent= delnode.parent
            elif delnode.isRightChilde():
                if delnode.leftChild:
                    delnode.parent.rightChild= delnode.leftChild
                    delnode.leftChild.parent= delnode.parent
                else:
                    delnode.parent.rightChild= delnode.rightChild
                    delnode.rightChild.parent= delnode.parent
            else:
                raise ValueError('shouldnt reach here')


        
def MinHeapBuiltin(object):
    def __init__(self):
        self.h= []

    def push(self,item):
        heapq.heappush(self,item)

    def pop(self):
        heapq.heappop(self)

def MaxHeapBuiltin(MinHeapBuiltin):
    """Assumes numberical items

    to avoid this would need define a MaxHeapObject(item)
    that flips the __lt__ method of item
    """
    def __init__(self):
        self.h=[]

    def push(self,item):
        heapq.heappush(self,-item)

    def pop(self):
        heapq.heappop(self)


# Broken after I moved to 0 indexed and using deque as underlying Queue
class MinHeap(Queue):
    """Use python built in "heapq" to do this for real

    I implemented the classic way below, using an array to represent
    the tree

    If 1-indexed, 
    i_leftChild= i_parent*2
    i_parent= i_{left or right}Child //2
    """

    #def remove(self):
    #    return self.things.pop(1)

    # def __getitem__(self,i):
    #    return self.things[i]

    # def __setitem__(self,i,val):
    #    self.things[i]= val

    def insert(self,key):
        self.things.push(key)
        self.bubbleUp()

    def getMin(self):
        smallest= self.things[0]
        if self.size() >= 2:
            self.things[0]= self.things.pop()
            self.bubbleDown()
        return smallest

    def swap(self,i,j):
        tmp= self.things[i]
        self.things[i]= self.things[j]
        self.things[j]= tmp

    def bubbleUp(self):
        i=self.size()-1
        while i > 1:
            if self.things[i] < self.Parent(i):
                self.swap(i,self.iParent(i))
                i= self.iParent(i)

    def bubbleDown(self):
        i=1
        while(self.MinChild(i)):
            if self.MinChild(i) < self.things[i]:
                self.swap(i,self.iMinChild(i))
            # Either way, iterate to the next one
            i= self.iMinChild(i)

    def iParent(self,i):
        return (i-1)//2

    def iLeftChild(self,i):
        return i*2 + 1

    def iRightChild(self,i):
        return i*2 + 2

    def iMinChild(self,i):
        if self.iLeftChild(i) >= self.size():
            return None
        elif self.iRightChild(i) >= self.size():
            return self.iLeftChild(i)
        else:
            if self.LeftChild(i) < self.RightChild(i):
                return self.iLeftChild(i)
            else:
                return self.iRgihtChild(i)

    def Parent(self,i):
        return self.things[self.iParent(i)]

    def LeftChild(self,i):
        return self.things[self.iLeftChild(i)]

    def RightChild(self,i):
        return self.things[self.iRightChild(i)]

    def MinChild(self,i):
        if self.iMinChild(i):
            return self.things[self.iMinChild(i)]
        else:
            return None


class Vertex(object):
    """A single node with an adjanceny list"""
    def __init__(self,name=None,payload=None):
        self.name= name
        self.payload= payload
        self.aDict= {} # Stores vertex objs
        # Searching
        self.color= 'w' 
        self.parentName= None


    def addConn(self,names,wts=None):
        """list of keys,wts to add"""
        if not wts:
            wts= [1]*len(names)
        for name,wt in zip(names,wts):
            self.aDict[name]= wt

class Graph(object):
    """Set of Vertices"""
    def __init__(self):
        self.vDict= {}

    def __getitem__(self,key):
        """g= Graph()
           g.vDict[key]= 10
           a= g[key]
        """
        return self.vDict[key]

    def __setitem__(self,key,val):
        """g= Graph()
           g[key]= val
        """
        self.vDict[key]= val

    def add(self,vName):
        self[vName]= Vertex(vName)

    def print_path(self,startName):
        v= self[startName]
        path='%s->' % v.name
        while v.parentName:
            v= self[v.parentName]
            path+= '%s->' % v.name
        print(path)


def BreadthFirst(graph,startName,findName):
    Q= Queue()
    v= graph[startName]
    Q.push(v)
    v.color='g'
    while not Q.isEmpty():
        checkV = Q.pop()
        if checkV.name == findName:
            return
        checkV.color='b'
        for name in checkV.aDict.keys():
            v= graph[name]
            if v.color == 'w':
                Q.push(v)
                v.color='g'
                v.parentName= checkV.name

def DepthFirst(graph, startName,findName):
    v= graph[startName]
    if v.name == findName:
        return
    v.color='g'
    for name in v.aDict.keys():
        newV= graph[name]
        if newV.color == 'w':
            newV.parentName= v.name
            DepthFirst(graph,newV.name,findName)
    v.color='b'

def graph_main():
    v= Vertex()
    for key in ['hey','there','kaylan']:
        v.add(key)
    v.children[0].add('my')
    v.children[0].children[0].add('name is Sean')

class test_binarytree(unittest.TestCase):
    def setUp(self):
        self.t= BinaryTree('A')
        self.t.insertLeft('B')
        self.t.insertRight('C')
        self.t.leftChild.insertLeft('D')
        self.t.leftChild.insertRight('E')
        self.t.rightChild.insertLeft('F')
        self.t.rightChild.insertRight('G')

    def test_traverse(self):
        print('pre')
        tree_traverse(self.t,how='pre')
        print('post')
        tree_traverse(self.t,how='post')
        print('in')
        tree_traverse(self.t,how='in')

class test_minheap(unittest.TestCase):
    def setUp(self):
        self.h= MinHeap()

    def test_minheap(self):
        for val in 'ABC':
            self.h.push(val)
        print('minheap= ',self.h.things)
        #for _ in range(self.h.size()-1):
        for val in 'ABC':
            self.assertEqual(self.h.getMin(),val)
        print(self.h)

        
class test_BST(unittest.TestCase):
    def setUp(self):
        print('test_BST')
        self.bst= BST()
        for key,val2store in zip([5, 30, 2, 25, 4,40],
                                 [None,None,None,None,'kaylan',None]):
            self.bst.insert(key,val2store)

    def test_bst_leaf_onechild(self):
        print('pre')
        tree_traverse(self.bst.root,how='pre')#,
        print('in')
        tree_traverse(self.bst.root,how='in')#,
                      #visit_func=lambda node: print(node.key,node.val2store))
        print(self.bst.get(25))
        # Leaf, left child
        self.bst.delete(25)
        print('deleted 25')
        tree_traverse(self.bst.root,how='in')
        # Leaf, right child
        self.bst.delete(4)
        print('deleted 4')
        tree_traverse(self.bst.root,how='in')
        # one child
        self.bst.insert(4,None)
        print('added 4')
        self.bst.delete(2)
        print('deleted 2')
        tree_traverse(self.bst.root,how='in')
        # one child, root
        self.bst.delete(4)
        self.bst.delete(5)
        print('deleted 5, one child root')
        tree_traverse(self.bst.root,how='in')

    # def test_bst_bothchildren(self):
    #     print('both: in')
    #     tree_traverse(self.bst.root,how='in')
    #     self.bst.delete(30)
    #     print('deleted 30')
    #     tree_traverse(self.bst.root,how='in')

class test_Graph(unittest.TestCase):
    def setUp(self):
        self.g= Graph()
        for i in range(6):
            self.g.add('V%d' % i)
        self.g['V0'].addConn(['V1','V5'])
        self.g['V1'].addConn(['V2'])
        self.g['V2'].addConn(['V3'])
        self.g['V3'].addConn(['V4','V5'])
        self.g['V4'].addConn(['V0'])
        self.g['V5'].addConn(['V2','V4'])

    def test_vertex_conn(self):
        print('graph has vertices:',self.g.vDict.keys())
        #self.assertEqual(self.g['V0'],dict(V1=1,V4=1,V5=1))
        for name in self.g.vDict.keys():
            print("%s connected to " % name, self.g[name].aDict.keys())

    def test_BFS(self):
        print('Breadth FS')
        findName='V0'
        BreadthFirst(self.g,startName='V1',findName=findName)
        self.g.print_path(findName)


    def test_DFS(self):
        print('DEPTH FS')
        findName='V0'
        DepthFirst(self.g,startName='V1',findName=findName)
        self.g.print_path(findName)



class test_heapq(unittest.TestCase):
    import heapq
    h= []
    for val in [('C',range(10)),
                ('B',range(20)),
                ('A',range(20,30))]:
        heapq.heappush(h,val)
    print('unsorted',h)
    print('sorted')
    while h:
        minima= heapq.heappop(h)
        print(minima[0])

    import numpy as np
    vals= np.random.randint(0,100,size=10)
    for val in vals:
        heapq.heappush(h,val)
    print(vals)
    print(heapq.nsmallest(4,h))


if __name__ == '__main__':
    unittest.main()
    

    
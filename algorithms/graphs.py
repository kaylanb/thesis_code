import unittest

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

    def hasOneChild(self):
        print('hasOne, left=, right=',self.leftChild,self.rightChild)
        return (self.leftChild and not self.rightChild) or \
               (self.rightChild and not self.leftChild)


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

    def delete(self,key):
        """Set references to this node to None"""
        delnode= self._get(key,self.root)
        if not delnode:
            raise KeyError('key=%s not in tree, cannot delete' % key)
        if delnode.isLeaf():
            if delnode.isLeftChild():
                delnode.parent.leftChild= None
            else:
                delnode.parent.rightChild= None
        print('left,right',delnode.leftChild,delnode.rightChild)
        a=delnode.hasOneChild()
        elif delnode.hasOneChild():
            if delnode.isLeftChild():
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
                # it is root, overwrite delnode
                if delnode.leftChild:
                    delnode.overwrite_with(delnode.leftChild)
                else:
                    delnode.overwrite_with(delnode.rightChild)
        elif delnode.hasBothChildren():
            pass
        else:
            rasie ValueError('Should not be able to get here')


        



class MinHeap(Queue):
    """classic way using a queue, not more intuitive binary tree

    If 1-indexed, 
    i_leftChild= i_parent*2
    i_parent= i_{left or right}Child //2
    """
    def __init__(self):
        super().__init__()
        self.add(None) # 1-indexed

    def remove(self):
        return self.things.pop(1)

    def __getitem__(self,i):
        return self.things[i]

    def __setitem__(self,i,val):
        self.things[i]= val

    def insert(self,key):
        self.add(key)
        self.bubbleUp()

    def getMin(self):
        mn= self.things[1]
        if self.size() >= 3:
            self.things[1]= self.things.pop(self.size()-1)
            self.bubbleDown()
        return mn

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
        return i//2

    def iLeftChild(self,i):
        return i*2

    def iRightChild(self,i):
        return self.iLeftChild(i) + 1

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
    def __init__(self,key=None):
        self.key= key
        self.children= [] 

    def add(self,key):
        self.children.append(Vertex(key))
        self.children[-1].children.append(self)

def BreadthFirst(graph,key_to_find):
    """graph is connected vertices"""
    Q= Queue()
    Q.add(graph.key)
    while not Q.isEmpty():
        key= Q.remove()
        if key == key_to_find:
            return key
        for child in graph.children:
            Q.add(child)

# Do we need a Queeu?
def DepthFirst(graph, key_to_find):
    """graph is connected vertices"""
    Q= Queue()
    Q.add(graph.key)
    while not Q.isEmpty():
        key= Q.remove()
        if key == key_to_find:
            return key
        for child in graph.children:
            found= DepthFirst(child,key_to_find)
            if found:
                return found

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
        self.h.insert('C')
        self.h.insert('B')
        self.h.insert('A')
        print('minheap= ',self.h.things)
        #for _ in range(self.h.size()-1):
        print(self.h.getMin())
        print('minheap= ',self.h.things)
        print(self.h.getMin())
        print('minheap= ',self.h.things)
        print(self.h.getMin())
        print('minheap= ',self.h.things)
        
class test_BST(unittest.TestCase):
    def setUp(self):
        print('test_BST')
        self.bst= BST()
        for key,val2store in zip([5, 30, 2, 25, 4],
                                 [None,None,None,None,'kaylan',None]):
            self.bst.insert(key,val2store)

    def test_bst(self):
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




if __name__ == '__main__':
    unittest.main()


    
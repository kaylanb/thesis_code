//Next steps:
//replace type std::string (key,val2store) in BinaryNode with template for any type
//use integer BST test case from graph.py
//finishh BST in this cpp module
//convert min heap to cpp
//convert Graph BFS and DFS to cpp

#include <iostream>

class BinaryNode {
public:
  std::string key;
  BinaryNode * leftChild;
  BinaryNode * rightChild;
  BinaryNode * parent;
  std::string val2store;

  BinaryNode(std::string Key) {key=Key;
                               leftChild=nullptr;
                               rightChild=nullptr;
                               parent=nullptr;
                               val2store="";}
  BinaryNode(std::string Key, BinaryNode *& Parent) 
                              {key=Key;
                               leftChild=nullptr;
                               rightChild=nullptr;
                               parent=Parent;
                               val2store="";}
  void insertLeft(std::string name);
  void insertRight(std::string name);
  bool isLeftChild();
  bool isRightChild();
  bool isRoot();
  bool isLeaf();
  bool hasBothChildren();
  void overwrite_with(BinaryNode *& node);
};

void BinaryNode::insertLeft(std::string name) {
  BinaryNode * node= new BinaryNode(name);
  if (leftChild) {
    node->leftChild= leftChild;
    leftChild= node;
  } else {
    leftChild= node;
  }
}

void BinaryNode::insertRight(std::string name) {
  BinaryNode * node= new BinaryNode(name);
  if (rightChild) {
    node->rightChild= rightChild;
    rightChild= node;
  } else {
    rightChild= node;
  }
}

bool BinaryNode::isLeftChild() {
  return this == this->parent->leftChild;
}

bool BinaryNode::isRightChild() {
  return this == this->parent->rightChild;
}

bool BinaryNode::isRoot() {
  return not this->parent;
}

bool BinaryNode::isLeaf() {
  return (!this->leftChild) && (!this->rightChild);
}

bool BinaryNode::hasBothChildren() {
    return (leftChild) && (rightChild);
}

void BinaryNode::overwrite_with(BinaryNode *& node) {
  this->key= node->key;
  this->leftChild= node->leftChild;
  this->rightChild= node->rightChild;
  this->val2store= node->val2store;
  this->parent= node->parent;
}



void visit(BinaryNode *& node) {
  std::cout << node->key << "\n";
}

//how: pre,post,in
void tree_traverse(BinaryNode *& node,
                   std::string how) {
  if (node) {
    if (how == "pre") {
      visit(node);
      tree_traverse(node->leftChild,how);
      tree_traverse(node->rightChild,how);
    } else if (how == "post") {
      tree_traverse(node->leftChild,how);
      tree_traverse(node->rightChild,how);
      visit(node);
    } else if (how == "in") {
      tree_traverse(node->leftChild,how);
      visit(node);
      tree_traverse(node->rightChild,how);
    }
  }
}

class BST {
public:
  BinaryNode * root;

  BST() {root=nullptr;}
  void insert(std::string key);
  void _insert(std::string key, BinaryNode *& node);
};

void BST::insert(std::string key) {
  if (!root)
      root= new BinaryNode(key);
  else
      _insert(key,root);
}

void BST::_insert(std::string key, BinaryNode *& node) {
  if (key < node->key) {
    if (node->leftChild)
      _insert(key,node->leftChild);
    else
      node->leftChild= new BinaryNode(key,node); //parent=node
  } 
  else {
    if (node->rightChild)
      _insert(key,node->rightChild);
    else
      node->rightChild= new BinaryNode(key,node);//parent=node
  }
}


//TESTS

void test_binarytree() {
  BinaryNode * t= new BinaryNode("A");
  t->insertLeft("B");
  t->insertRight("C");
  t->leftChild->insertLeft("D");
  t->leftChild->insertRight("E");
  t->rightChild->insertLeft("F");
  t->rightChild->insertRight("G");

  // Traverse
  std::string how = "pre";
  std::cout << how << "\n";
  tree_traverse(t,how);
  how= "post";
  std::cout << how << "\n";
  tree_traverse(t,how);
  how="in";
  std::cout << how << "\n";
  tree_traverse(t,how);
}

void test_BST() {
  std::cout << "test_BST\n";
  BST * bst= new BST();
  std::string keys[] = {"B", "D", "A", "C","E"};
  for (int i=0; i<5; i++)
    bst->insert(keys[i]);

  //leaf or onechild
  std::cout << "pre\n";
  tree_traverse(bst->root,"pre");
  std::cout << "in\n";
  tree_traverse(bst->root,"in");
}

int main() {
  //test_binarytree();
  test_BST();
  return 0;
}
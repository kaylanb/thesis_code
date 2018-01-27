#include <iostream>

class BinaryTree {
public:
  std::string key;
  BinaryTree * leftChild;
  BinaryTree * rightChild;

  BinaryTree(std::string name);
  void insertLeft(std::string name);
  void insertRight(std::string name);
};

BinaryTree::BinaryTree(std::string name) {
  key= name;
  leftChild= nullptr;
  rightChild= nullptr;
}

void BinaryTree::insertLeft(std::string name) {
  BinaryTree * node= new BinaryTree(name);
  if (leftChild) {
    node->leftChild= leftChild;
    leftChild= node;
  } else {
    leftChild= node;
  }
}

void BinaryTree::insertRight(std::string name) {
  BinaryTree * node= new BinaryTree(name);
  if (rightChild) {
    node->rightChild= rightChild;
    rightChild= node;
  } else {
    rightChild= node;
  }
}

void visit(BinaryTree *& node) {
  std::cout << node->key << "\n";
}

//how: pre,post,in
void tree_traverse(BinaryTree *& node,
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


class bstNode: BinaryTree {
public:
  BinaryTree * parent;
  string val2store;

  bstNode(std::string name);
};

bstNode::bstNode(std::string name) {
  //name,leftChild,rightChild from BinaryTree
  parent= nullptr;
  val2store= std::string();
}

bool isLeftChild() {
  return this == this->parent->leftChild;
}

bool isRightChild() {
  return this == this->parent->rightChild;
}

bool isRoot() {
  return not this->parent;
}

bool isLeaf() {
  return (!this->leftChild) && (!this->rightChild);
}

bool hasBothChildren() {
    return (leftChild) && (rightChild);
}

void overwrite_with(bstNode * node) {
  this->key= node->key;
  this->leftChild= node->leftChild;
  this->rightChild= node->rightChild;
  this->val2store= node->val2store;
  this->parent= node->parent;
}


//TESTS

void test_binarytree() {
  BinaryTree * t= new BinaryTree("A");
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

int main() {
  test_binarytree();
  return 0;
}
//clang++ -std=c++11 -stdlib=libc++ linking_nodes.cpp -o linking_nodes
//https://www.codementor.io/codementorteam/a-comprehensive-guide-to-implementation-of-singly-linked-list-using-c_plus_plus-ondlm5azr
#include <iostream>
#include <array>
#include <cassert>
using namespace std;

// Attributes:
//   data, next
struct Node {
  int val;
  Node * next;

  Node(int data=NULL);
};

Node::Node(int data) {
    val= data;
    next= nullptr;
}

// Attributes:
//   head
class LinkedList {
  Node * head;

  public:
    LinkedList();
    void insert(int d);
    int remove(int d); 
    int next();
};

LinkedList::LinkedList() {
  head = new Node();
}

void LinkedList::insert(int d) {
  cout << "inserting val=" << d << '\n';
  Node * new_node = new Node(d);
  new_node->next= head; 
  head= new_node;
}

int LinkedList::remove(int d) {
  Node * curr = head;
  Node * prev = nullptr;
  while(curr) {
    if (curr->val == d) {
        if (prev)
            prev->next= curr->next;
        else
            head = curr->next;
        delete(curr);
        cout << "removed val=" << d << '\n';
        return d;
    }
    prev= curr;
    curr= curr->next;
  }
  cout << "WARNING, nothing with val = " << d << "to remove";
  return 1;
}

int LinkedList::next() {
  return head->val;
}

void test_LinkedList() {
  LinkedList ll;

  array<int,3> data {10,5,-1};  
  for (int i=0 ; i< data.size() ; ++i ) {
    ll.insert(data[i]);
    assert(ll.next() == data[i]);
  }
  for (int i=0; i<data.size(); i++) {
    assert(ll.remove(data[i]) == data[i]);
  }
  assert(!ll.next());
}

int main() {
  test_LinkedList(); 

  return 0;
}
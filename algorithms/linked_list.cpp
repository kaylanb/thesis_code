//clang++ -std=c++11 -stdlib=libc++ linked_list.cpp -o linked_list
//https://www.codementor.io/codementorteam/a-comprehensive-guide-to-implementation-of-singly-linked-list-using-c_plus_plus-ondlm5azr
#include <iostream>
#include <array>
#include <cassert>
using namespace std;

// Attributes:
//   data, next
struct Node {
  int data;
  Node * next;

  Node(int d);
};

Node::Node(int d) {
    data= d;
    next= nullptr;
}

// Attributes:
//   head
class LinkedList {
  public:
    Node * head = nullptr; //new Node(0);
    //LinkedList();
    void insert(int d);
    int remove(int d); 
};

void LinkedList::insert(int d) {
  cout << "inserting data=" << d << '\n';
  Node * new_node = new Node(d);
  new_node->next= head; 
  head= new_node;
}
// delete the Node that has Node.data == data
int LinkedList::remove(int d) {
  cout << "removing data=" << d << '\n';
  Node * curr_node = head;
  Node * prev_node = nullptr;
  while(curr_node) {
    if (curr_node->data == d) {
        if (prev_node)
            prev_node->next= curr_node->next;
        else
            head = curr_node->next;
        delete(curr_node);
        return 0;
    }
    prev_node= curr_node;
    curr_node= curr_node->next;
  }
  return 1;
}

void test_LinkedList() {
  LinkedList ll;

  array<int,3> data {10,5,-1};  
  for (int i=0 ; i< data.size() ; ++i ) {
    ll.insert(data[i]);
  }

  assert(ll.head->data == -1);
  assert(ll.head->next->data == 5);
  assert(ll.head->next->next->data == 10);

  ll.remove(5);
  assert(ll.head->data == -1);
  assert(ll.head->next->data == 10);
}


int main() {
  test_LinkedList(); 

  return 0;
}
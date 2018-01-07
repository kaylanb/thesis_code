//clang++ -std=c++11 -stdlib=libc++ linked_list.cpp -o linked_list
//https://www.codementor.io/codementorteam/a-comprehensive-guide-to-implementation-of-singly-linked-list-using-c_plus_plus-ondlm5azr
#include <iostream>
#include <array>
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
    Node * head = new Node(0);
    //LinkedList();
    void insert(int d);
    //void remove(int data); 
    void printList();
};

// LinkedList::LinkedList() {
//     head->next = nullptr;
// } 
void LinkedList::insert(int d) {
  cout << "inserting data=" << d << '\n';
  Node * new_node = new Node(d);
  cout << "new_node->data= " << new_node->data << '\n';
  cout << "new_node->next= " << new_node->next << '\n';
  cout << "head->next= " << head->next << '\n';
  new_node->next= head->next;
  head->next= new_node;
}
void LinkedList::printList() {
  while(head) {
    std::cout << head->data << "-->";
    head = head->next;
  }
  std::cout << "null" << std::endl;
}


int main() {
  //Node * new_node = new Node(10);
  //cout << "node.data=" << new_node.data;

  LinkedList ll;
  //ll.printList();

  array<int,3> data {10,5,-1};
  cout << "data: \n";
  for (int val : data)
    cout << val << '\n';
  
  for (int i=0 ; i<data.size() ; ++i ) {
    ll.insert(data[i]);
  }

  return 0;
}
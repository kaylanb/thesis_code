//clang++ -std=c++11 -stdlib=libc++ linking_nodes.cpp -o linking_nodes
//https://www.codementor.io/codementorteam/a-comprehensive-guide-to-implementation-of-singly-linked-list-using-c_plus_plus-ondlm5azr
#include <iostream>
#include <array>
#include <cassert>
#include <list>

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
  protected:
    Node * head;

  public:
    LinkedList();
    void insert(int d);
    int remove(int d); 
    int next();
    bool isEmpty();
};

LinkedList::LinkedList() {
  head = nullptr;
}

void LinkedList::insert(int d) {
  std::cout << "inserting val=" << d << '\n';
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
        std::cout << "removed val=" << d << '\n';
        return d;
    }
    prev= curr;
    curr= curr->next;
  }
  std::cout << "WARNING, nothing with val = " << d << "to remove";
  return 1;
}

int LinkedList::next() {
  if (isEmpty())
    return NULL;
  else
    return head->val;
}

bool LinkedList::isEmpty() {
  return head == nullptr;
}


class Stack: public LinkedList {

  public:
    void add(int data);
    int pop();
};

void Stack::add(int data) {
  insert(data);
} 

int Stack::pop() {
  Node * del_node= head;
  head= head->next;
  int val= del_node->val;
  delete del_node;
  std::cout << "deleting value = " << val << "\n";
  return val;
} 


class Queue {
  Node * first;
  Node * last;

  public:
    Queue();
    void add(int data);
    int pop();
    int next();
    bool isEmpty();
};

Queue::Queue() {
  // LinkedLIst constructor
  first= nullptr;
  last= nullptr;
}

// Insert at the end
void Queue::add(int data) {
  std::cout << "inserting val=" << data << "\n";
  Node * new_node= new Node(data);
  if (last != nullptr)
    last->next = new_node;
  last= new_node;
  if (first == nullptr)
    first= new_node;
}

// remove from beginning
int Queue::pop() {
  Node * del_node= first;
  first= first->next;
  if (first == nullptr) {
    last= nullptr;
  }
  int val= del_node->val;
  delete del_node;
  std::cout << "deleting value = " << val << "\n";
  return val;
}

int Queue::next() {
  return first->val;
}

bool Queue::isEmpty() {
  return first == nullptr;
}


class QueueLL {
  std::list<int> q;

  public:
    void add(int data);
    int pop();
    bool isEmpty();
    int next();
};

void QueueLL::add(int data) {
  std::cout << "adding val=" << data << "\n";
  q.push_back(data);
}

int QueueLL::pop() {
  int f= *q.begin();
  q.pop_front();
  std::cout << "deleting val = " << f << "\n";
  return f;
}

bool QueueLL::isEmpty() {
  return q.empty();
}

int QueueLL::next() {
  return *q.begin();
}



void test_LinkedList() {
  LinkedList ll;

  std::array<int,3> data {10,5,-1};  
  for (int i=0 ; i< data.size() ; ++i ) {
    ll.insert(data[i]);
    assert(ll.next() == data[i]);
  }
  for (int i=0; i<data.size(); i++) {
    assert(ll.remove(data[i]) == data[i]);
  }
  std::cout << "hey\n";
  assert(ll.isEmpty());
}

void test_Stack() {
  Stack s;

  std::array<int,3> data {10,5,-1};  
  for (int i=0 ; i< data.size() ; ++i ) {
    s.add(data[i]);
    assert(s.next() == data[i]);
  }
  for (int i=data.size()-1; i>=0; --i) {
    assert(s.pop() == data[i]);
  }
  assert(s.isEmpty());
}

void test_Queue() {
  std::array<int,3> data {10,5,-1};  
  Queue q;
  
  for (int i=0; i<data.size(); i++) {
    q.add(data[i]);
    assert(q.next() == data[0]);
  }
  for (int i=0; i<data.size(); i++) {
    assert(q.pop() == data[i]);
  }
  assert(q.isEmpty());
}

void test_QueueLL() {
  std::array<int,3> data {10,5,-1};  
  QueueLL q;
  
  for (int i=0; i<data.size(); i++) {
    q.add(data[i]);
    assert(q.next() == data[0]);
  }
  for (int i=0; i<data.size(); i++) {
    assert(q.pop() == data[i]);
  }
  assert(q.isEmpty());
}

int main() {
  std::cout << "linkedlist\n";
  test_LinkedList();
  std::cout << "stack\n";
  test_Stack(); 
  std::cout << "queue\n";
  test_Queue(); 
  std::cout << "queueLL\n";
  test_QueueLL();

  return 0;
}
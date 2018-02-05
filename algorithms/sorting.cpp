//clang++ -std=c++11 -stdlib=libc++ linking_nodes.cpp -o linking_nodes
//http://interactivepython.org/runestone/static/pythonds/SortSearch/toctree.html
#include <iostream>
#include <vector>
#include <cassert>

void print_vector(std::vector<int>& v) {
  for (auto it=v.begin(); it<v.end(); it++) {
    std::cout << *it << " ";
  }
  std::cout << "\n";
} 

void print_vector_i(std::vector<int>& v,
                    int istart,int istop) {
  for (int i= istart; i<=istop; i++) {
    std::cout << v.at(i) << " ";
  }
  std::cout << "\n";
} 

// iterate through list, compare current to next, swap if <
// repeat for len list -1 times
void bubbleSort(std::vector<int>& v) { 
  bool need_sort=true;
  while(need_sort) {
    need_sort=false;
    for (auto it=v.begin(); it<v.end()-1; it++) {
      if (*(it+1) < *it) {
        need_sort=true;
        int tmp= *it;
        *it= *(it+1);
        *(it+1)= tmp;
      }
    }
  }
}

// iterate through array N times, put min element at front, or max at end
// after each iteration
void selectionSort(std::vector<int>& v) {
  for (int sweep=0; sweep<v.size(); sweep++) {
    int imin=sweep;
    for (int i=imin+1; i<v.size(); i++ ) {
      if (v[i] < v[imin]) {
        imin= i;
      }
    }
    int tmp= v[sweep];
    v[sweep]= v[imin];
    v[imin]= tmp;
  }
}

// std::vector<int> insertion(std::vector<int>& a) {
//   std::vector<int> v= a;

//   for (int next=1; next<v.size(); next++){
//     for (int start=0; start<next; start++) {
//       if v[next] < v[start] {
//         int tmp= v[start];
//         v[start]= v[next];
//         v[next]= tmp;
//         // move the remaining to the right

//         break;
//       }
//     }
//   }
//   return v;
// }

//std::vector<int>::iterator it_start,
//                             std::vector<int>::iterator it_end) {
std::vector<int> copy_vector(std::vector<int>& v,
                             int istart,int istop) {
  std::vector<int> v2;
  //for (auto it=it_start; it<=it_end; it++) {
  for (int i=istart; i<=istop; i++) {
    v2.push_back(v.at(i));
  }
  return v2;
}

void mergeSort(std::vector<int>& v) {
  // std::cout << "splitting list=";
  // print_vector(v);
  if (v.size() > 1) {
    int imid= (v.size()-1)/2;
    std::vector<int> left= copy_vector(v,0,imid);
    std::vector<int> right= copy_vector(v,imid+1,v.size()-1);
    
    mergeSort(left);
    mergeSort(right);

    // std::cout << "left(" << left.size() << ")= ";
    // print_vector(left);
    // std::cout << "right(" << right.size() << ")= ";
    // print_vector(right);
    // std::cout << "v(" << v.size() << ")= ";
    // print_vector(v);
    //merge
    int p=0, L=0, R=0;
    while (L<left.size() && R<right.size()) {
      if (left.at(L) < right.at(R)) {
        v.at(p)= left.at(L);
        L++;
      }
      else {
        v.at(p)= right.at(R);
        R++;
      }
      p++;
    }
    while(L<left.size()) {
      v.at(p)= left.at(L);
      p++;
      L++;
    }
    while(R<right.size()) {
      v.at(p)= right.at(R);
      p++;
      R++;
    }
  }
  // std::cout << "merged list=";
  // print_vector(v);
}

void quickSort_main(std::vector<int>& v,
                    int istart,int iend) {
  // std::cout << "input= ";
  // print_vector_i(v,istart,iend);
  // std::cout << "full vector= ";
  // print_vector(v);
  if (iend > istart) {
    //partition: elem < pivot on left, elem > pivot on right 
    //(not sorted yet)
    int p=istart; 
    int L=p+1,R=iend;
    while (L < R) {
      // move as far right as can
      while (v.at(L) <= v.at(p)) {
        L++;
      }
      while (v.at(R) > v.at(p)) {
        R--;
      }
      // break standoff
      if (L< R) {
        int tmp=v.at(L);
        v.at(L)= v.at(R);
        v.at(R)= tmp;
      }
    }
    int tmp=v.at(R);
    v.at(R)= v.at(p);
    v.at(p)= tmp;
    //std::cout << "splitpt=" << R << " partioned= ";
    //print_vector_i(v,istart,iend);

    //partition left and right respectively -> (sorted)
    quickSort_main(v,istart,R-1);
    quickSort_main(v,R+1,iend);
  }
}

void quickSort(std::vector<int>& v) {
  quickSort_main(v,0,v.size()-1);
}

void print_sorted(void (*sortFunc)(std::vector<int>&),
                  std::vector<int>& v, const char * name) {  
  std::vector<int> v2= v;
  sortFunc(v2);
  std::cout << name << ": ";
  print_vector(v2);
}

void test_sorting() {
  std::vector<int> v {6,2,7,5,-1,10,3};  
  print_vector(v);
  print_sorted(bubbleSort,v,"bubble");
  print_vector(v);
  print_sorted(selectionSort,v,"selection");
  print_vector(v);
  print_sorted(mergeSort,v,"mergeSort");
  print_vector(v);
  print_sorted(quickSort,v,"quickSort");
}

int main() {
  test_sorting();

  return 0;
}
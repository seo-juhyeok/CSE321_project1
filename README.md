# B-tree implementation
**CSE32101 project1**

## This project implement B-tree, B+-tree, B*-tree

## environment
* Language: Python 3.10.2
* Dataset: The 'student.csv' file must be located in the same directory to ensure the program runs correctly.
* Data format: The CSV file data should have this structure: Student ID, Name, Gender, GPA, Height, Weight.

## Operation
* You can choose the tree type(1: B-tree, 2: B+-tree, 3: B*-tree) and order(order should be larger than 2).
* After select the tree you can do 6 operation.
1. **search**: display the full data of a student with input student ID.
2. **insert**: add a new student record to the tree by providing data in the format: Student ID, Name, Gender, GPA, Height, Weight.
3. **delete**: Remove a student record from the tree using their Student ID.
4. **Advanced Operations & Performance Testing**
  * 4-1. point search: Execute a specified number of random searches to measure and display total and average search times.
  * 4-2. range query: Filter female students with IDs between 202000000 and 202400000, calculating their average GPA and height while measuring execution time.
  * 4-3. delete multiple IDs: Randomly delete a specified number of keys from the tree and evaluate the execution time.
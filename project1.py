import csv
import random
import time

 # ============================================
 # B-tree
 # ============================================

class Btree_node:
    def __init__(self, leaf = False):
        self.leaf = leaf
        self.keys = []
        self.pointers = []
        self.children = []
class Btree:
    def __init__(self, order):
        self.root = Btree_node(leaf = True)
        self.order = order

    def search(self, node, searching_key):
        i = 0
        while searching_key > node.keys[i]:
            i += 1
            if i >= len(node.keys):
                break
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                return node.pointers[i]
        if node.leaf == True:
            return None
        else:
            return self.search(node.children[i], searching_key)
        
    def where_to_insert(self, inserting_key):
        path = []
        index_list = []
        location = self.root
        while location.leaf == False:
            i = 0
            while inserting_key > location.keys[i]:
                i += 1
                if i >= len(location.keys):
                    break
            path.append(location)
            index_list.append(i)
            location = location.children[i]
        return location, path, index_list

    def key_insert(self, inserting_key, pointer):
        location, path, index_list = self.where_to_insert(inserting_key)
        i = 0
        while (i < len(location.keys)) and (location.keys[i] < inserting_key):
            i += 1
        location.keys.insert(i, inserting_key)
        location.pointers.insert(i, pointer)

        while len(location.keys) >= self.order:
            mid = len(location.keys) // 2
            mid_key = location.keys[mid]
            mid_pointer = location.pointers[mid]
            right_node = Btree_node(leaf = location.leaf)
            right_node.keys = location.keys[mid+1:]
            right_node.pointers = location.pointers[mid+1:]
            if location.leaf == False:
                right_node.children = location.children[mid+1:]
                location.children = location.children[:mid+1]
            location.keys = location.keys[:mid]
            location.pointers = location.pointers[:mid]
            if len(path) == 0:
                new_root = Btree_node(leaf = False)
                new_root.keys.append(mid_key)
                new_root.pointers.append(mid_pointer)
                new_root.children.append(location)
                new_root.children.append(right_node)
                self.root = new_root
                return
            parent = path.pop()
            index = index_list.pop()
            parent.keys.insert(index, mid_key)
            parent.pointers.insert(index, mid_pointer)
            parent.children.insert(index + 1, right_node)
            location = parent
    def key_delete(self, deleting_key):
        pass
    def range_query(self, node, result_list):
        i = 0
        while (i < len(node.keys)) and (node.keys[i] < 202000000):
            i += 1
        while (i < len(node.keys)) and (node.keys[i] <= 202400000):
            if node.leaf == False:
                self.range_query(node.children[i], result_list)
            result_list.append(node.pointers[i])
            i += 1
        if node.leaf == False:
            self.range_query(node.children[i], result_list)

 # ============================================
 # B+-tree
 # ============================================

class Bplus_tree_node:
    def __init__(self, leaf = False):
        self.leaf = leaf
        self.keys = []
        self.pointers = []
        self.children = []
        self.next = None
class Bplus_tree:
    def __init__(self, order):
        self.root = Bplus_tree_node(leaf = True)
        self.order = order

    def search(self, node, searching_key):
        i = 0
        while searching_key >= node.keys[i]:
            i += 1
            if i >= len(node.keys):
                break
        if node.leaf == True:
            if (i > 0) and (node.keys[i-1] == searching_key):
                return node.pointers[i-1]
            else:
                return None
        else:
            return self.search(node.children[i], searching_key)
        
    def where_to_insert(self, inserting_key):
        path = []
        index_list = []
        location = self.root
        while location.leaf == False:
            i = 0
            while inserting_key >= location.keys[i]:
                i += 1
                if i >= len(location.keys):
                    break
            path.append(location)
            index_list.append(i)
            location = location.children[i]
        return location, path, index_list

    def key_insert(self, inserting_key, pointer):
        location, path, index_list = self.where_to_insert(inserting_key)
        i = 0
        while (i < len(location.keys)) and (location.keys[i] < inserting_key):
            i += 1
        location.keys.insert(i, inserting_key)
        location.pointers.insert(i, pointer)

        while len(location.keys) >= self.order:
            mid = len(location.keys) // 2
            mid_key = location.keys[mid]
            right_node = Bplus_tree_node(leaf = location.leaf)
            if location.leaf == True:
                right_node.keys = location.keys[mid:]
                right_node.pointers = location.pointers[mid:]
                location.keys = location.keys[:mid]
                location.pointers = location.pointers[:mid]
                right_node.next = location.next
                location.next = right_node
            else:
                right_node.keys = location.keys[mid+1:]
                right_node.children = location.children[mid+1:]
                location.keys = location.keys[:mid]
                location.children = location.children[:mid+1]
            if len(path) == 0:
                new_root = Bplus_tree_node(leaf=False)
                new_root.keys.append(mid_key)
                new_root.children.append(location)
                new_root.children.append(right_node)
                self.root = new_root
                return
            parent = path.pop()
            index = index_list.pop()
            parent.keys.insert(index, mid_key)
            parent.children.insert(index + 1, right_node)
            location = parent
    def key_delete(self, deleting_key):
        pass
    def range_query(self, node, result_list):
        node = self.where_to_insert(202000000)[0]
        while True:
            for i in range(len(node.keys)):
                key = node.keys[i]
                if key > 202400000:
                    return result_list
                if 202000000 <= key:
                    result_list.append(node.pointers[i])
            node = node.next
            if node == None:
                break
        return result_list

 # ==========================================
 # Selecting tree type and fanout order, and measuring insertion time
 # ========================================== 

tree_type = input("which type of tree? (1: B-tree, 2: B+-tree, 3: B*-tree): ")
fanout_order = int(input("fanout order of tree: "))
if tree_type == '1': # B-tree
    tree = Btree(order = fanout_order)
elif tree_type == '2': # B+-tree
    tree = Bplus_tree(order = fanout_order)
elif tree_type == '3': # B*-tree
    tree = Btree(order = fanout_order)
student_info = []
file_path = 'student.csv'

with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    index = 0
    start_time = time.perf_counter()
    for row in reader:
        student_info.append(row)
        student_id = row['Student ID']
        tree.key_insert(int(student_id), index)
        index = index + 1
    end_time = time.perf_counter()
    print(f"insertion time: {end_time - start_time:.6f} seconds.")

 # ==========================================
 # Testing method
 # Selecting the operation and measuring the time for operations
 # ========================================== 
operation = input("which operation? (1: search, 2: insert, 3: delete, 4: others, 5: exit): ")
while operation != '5':
    if operation == '1': # search
        target_id = input("which student ID to search: ")
        result = tree.search(tree.root, int(target_id))
        if result != None:
            student_data = student_info[result]
            print(f"data: {student_data}")
        else:
            print("there is no student with that ID.")
    elif operation == '2': # insert
        data = input("which student data to insert (format: Student ID, Name, Gender, GPA, Height, Weight): ")
        student_id, name, gender, gpa, height, weight = data.split(', ')
        student_info.append({'Student ID': student_id, 'Name': name, 'Gender': gender, 'GPA': gpa, 'Height': height, 'Weight': weight})
        tree.key_insert(int(student_id), len(student_info) - 1)
    elif operation == '3': # delete
        pass
    elif operation == '4': # others
        detail_operation = input("which operation? (1: point search, 2: range query, 3: deletion & structural integrity): ")
        if detail_operation == '1': # point search
            num = int(input("how many point searches? "))
            student_ids = [int(row['Student ID']) for row in student_info]
            search_ids = random.sample(student_ids, num)
            start_time = time.perf_counter()
            for search_id in search_ids:
                tree.search(tree.root, search_id)
            end_time = time.perf_counter()
            print(f"total time: {end_time - start_time:.8f} seconds.")
            print(f"mean time: {(end_time - start_time) / num:.8f} seconds.")
        elif detail_operation == '2': # range query
            print("Calculate the average GPA and height of female students whose IDs are between 202000000 and 202400000.")
            range_query_result = []
            Gpa = 0
            height = 0
            count = 0
            start_time = time.perf_counter()
            tree.range_query(tree.root, range_query_result)
            for i in range(len(range_query_result)):
                student_data = student_info[range_query_result[i]]
                if student_data['Gender'] == 'Female':
                    Gpa += float(student_data['GPA'])
                    height += float(student_data['Height'])
                    count += 1
            end_time = time.perf_counter()
            print(f"Average GPA: {Gpa / count:.4f}")
            print(f"Average Height: {height / count:.4f}")
            print(f"total time: {end_time - start_time:.6f} seconds.")
        elif detail_operation == '3': # deletion & structural integrity
            pass
    operation = input("which operation? (1: search, 2: insert, 3: delete, 4: others, 5: exit): ")

 # test data
 # 202637934	Sungmin Chae	Male	3.6	    177.3	67.6
 # 202083002	Pamela Mitchell	Female	3.46	158     49.6
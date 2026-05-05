import csv
import random
import time
import math

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
        while (i < len(node.keys)) and (searching_key > node.keys[i]):
            i += 1
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                return node.pointers[i], node
        if node.leaf == True:
            return None, None
        else:
            return self.search(node.children[i], searching_key)
        
    def change_pointer(self, node, searching_key, new_pointer):
        i = 0
        while (i < len(node.keys)) and (searching_key > node.keys[i]):
            i += 1
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                node.pointers[i] = new_pointer
                return True
        if node.leaf == True:
            return False
        else:
            return self.change_pointer(node.children[i], searching_key, new_pointer)    
        
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

        while len(location.keys) >= self.order: # node split
            mid = len(location.keys) // 2
            mid_key = location.keys[mid]
            mid_pointer = location.pointers[mid]
            right_node = Btree_node(leaf = location.leaf)
            right_node.keys = location.keys[mid+1:]
            right_node.pointers = location.pointers[mid+1:]

            if location.leaf == False: # not leaf node
                right_node.children = location.children[mid+1:]
                location.children = location.children[:mid+1]
            location.keys = location.keys[:mid]
            location.pointers = location.pointers[:mid]

            if len(path) == 0: # root node
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

    def where_to_delete(self, node, searching_key, path, index_list):
        i = 0
        while (i < len(node.keys)) and (searching_key > node.keys[i]):
            i += 1
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                return node.pointers[i], node
        if node.leaf == True:
            return None, None
        else:
            path.append(node)
            index_list.append(i)
            return self.where_to_delete(node.children[i], searching_key, path, index_list)

    def satisfy_properties(self, node, path, index_list):
        min_keys = math.ceil(self.order / 2) - 1 

        if len(path) == 0: # root node
            if len(node.keys) == 0:
                if len(node.children) > 0:
                    self.root = node.children[0]
            return
        if len(node.keys) >= min_keys: # tree satisfy the properties
            return

        parent = path.pop()
        index = index_list.pop()
        if index == 0:
            left_sibling = None
            right_sibling = parent.children[index + 1]
        elif index == len(parent.children) - 1:
            left_sibling = parent.children[index - 1]
            right_sibling = None
        else:
            left_sibling = parent.children[index - 1]
            right_sibling = parent.children[index + 1]

        # distribution (borrow from sibling that has more keys)
        from_left = True
        if (left_sibling != None) and (len(left_sibling.keys) > min_keys) and (right_sibling != None) and (len(right_sibling.keys) > min_keys):
            if len(left_sibling.keys) < len(right_sibling.keys):
                from_left = False
        if (left_sibling != None) and (len(left_sibling.keys) > min_keys) and (from_left == True): # borrow from left sibling
            node.keys.insert(0, parent.keys[index - 1])
            node.pointers.insert(0, parent.pointers[index - 1])
            if node.leaf == False:
                node.children.insert(0, left_sibling.children.pop())
            parent.keys[index - 1] = left_sibling.keys.pop()
            parent.pointers[index - 1] = left_sibling.pointers.pop()
            return
        if (right_sibling != None) and (len(right_sibling.keys) > min_keys): # borrow from right sibling
            node.keys.append(parent.keys[index])
            node.pointers.append(parent.pointers[index])
            if node.leaf == False:
                node.children.append(right_sibling.children.pop(0))
            parent.keys[index] = right_sibling.keys.pop(0)
            parent.pointers[index] = right_sibling.pointers.pop(0)
            return

        # merge (if both siblings have only minimum number of keys)
        if left_sibling != None: # merge with left sibling
            left_sibling.keys.append(parent.keys.pop(index - 1))
            left_sibling.pointers.append(parent.pointers.pop(index - 1))
            left_sibling.keys.extend(node.keys)
            left_sibling.pointers.extend(node.pointers) 
            if node.leaf == False:
                left_sibling.children.extend(node.children)
            parent.children.pop(index)
            self.satisfy_properties(parent, path, index_list)
        else: # merge with right sibling
            node.keys.append(parent.keys.pop(index))
            node.pointers.append(parent.pointers.pop(index))
            node.keys.extend(right_sibling.keys)
            node.pointers.extend(right_sibling.pointers)
            if node.leaf == False:
                node.children.extend(right_sibling.children)
            parent.children.pop(index + 1)
            self.satisfy_properties(parent, path, index_list)
    
    def key_delete(self, deleting_key):
        path = []
        index_list = []
        pointer, delete_node = self.where_to_delete(self.root, deleting_key, path, index_list)
        if pointer == None:
            return None
        elif delete_node.leaf == False: # find the successor
            for i in range(len(delete_node.keys)):
                if delete_node.keys[i] == deleting_key:
                    path.append(delete_node)
                    index_list.append(i+1)
                    current_node = delete_node.children[i+1]
                    break
            while current_node.leaf == False:
                path.append(current_node)
                index_list.append(0)
                current_node = current_node.children[0]
            successor_key = current_node.keys[0]
            successor_pointer = current_node.pointers[0]
            for i in range(len(delete_node.keys)):
                if delete_node.keys[i] == deleting_key:
                    delete_node.keys[i] = successor_key
                    delete_node.pointers[i] = successor_pointer
                    break
            final_delete_node = current_node
            index_to_delete = 0
        else:
            for i in range(len(delete_node.keys)):
                if delete_node.keys[i] == deleting_key:
                    break
            final_delete_node = delete_node
            index_to_delete = i
        final_delete_node.keys.pop(index_to_delete)
        final_delete_node.pointers.pop(index_to_delete)

        self.satisfy_properties(final_delete_node, path, index_list)

        # update student_info
        last_index = len(student_info) - 1
        if pointer < last_index:
            last_student_id = int(student_info[-1]['Student ID'])
            student_info[pointer] = student_info[-1]
            self.change_pointer(self.root, last_student_id, pointer)
        student_info.pop()

        return pointer

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
                return node.pointers[i-1], node
            else:
                return None, None
        else:
            return self.search(node.children[i], searching_key)

    def change_pointer(self, node, searching_key, new_pointer):
        i = 0
        while (i < len(node.keys)) and (searching_key >= node.keys[i]):
            i += 1
        if node.leaf == True:
            if i != 0:
                if node.keys[i-1] == searching_key:
                    node.pointers[i-1] = new_pointer
                    return True
            return False
        else:
            return self.change_pointer(node.children[i], searching_key, new_pointer)

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

    def satisfy_properties(self, node, path, index_list):
        if node.leaf == False:
            min_keys = math.ceil(self.order / 2) - 1
        else:
            min_keys = math.ceil((self.order - 1) / 2)

        if len(path) == 0: # root node
            if len(node.keys) == 0:
                if len(node.children) > 0:
                    self.root = node.children[0]
            return
        if len(node.keys) >= min_keys: # tree satisfy the properties
            return

        parent = path.pop()
        index = index_list.pop()
        if index == 0:
            left_sibling = None
            right_sibling = parent.children[index + 1]
        elif index == len(parent.children) - 1:
            left_sibling = parent.children[index - 1]
            right_sibling = None
        else:
            left_sibling = parent.children[index - 1]
            right_sibling = parent.children[index + 1]

        # distribution (borrow from sibling that has more keys)
        from_left = True
        if (left_sibling != None) and (len(left_sibling.keys) > min_keys) and (right_sibling != None) and (len(right_sibling.keys) > min_keys):
            if len(left_sibling.keys) < len(right_sibling.keys):
                from_left = False
        if (left_sibling != None) and (len(left_sibling.keys) > min_keys) and (from_left == True): # borrow from left sibling
            if node.leaf == True:
                node.keys.insert(0, left_sibling.keys.pop())
                node.pointers.insert(0, left_sibling.pointers.pop())
                parent.keys[index - 1] = node.keys[0]
            else:
                node.keys.insert(0, parent.keys[index - 1])
                parent.keys[index - 1] = left_sibling.keys.pop()
                node.children.insert(0, left_sibling.children.pop())
            return
        if (right_sibling != None) and (len(right_sibling.keys) > min_keys): # borrow from right sibling
            if node.leaf == True:
                node.keys.append(right_sibling.keys.pop(0))
                node.pointers.append(right_sibling.pointers.pop(0))
                parent.keys[index] = right_sibling.keys[0]
            else:
                node.keys.append(parent.keys[index])
                parent.keys[index] = right_sibling.keys.pop(0)
                node.children.append(right_sibling.children.pop(0))
            return

        # merge (if both siblings have only minimum number of keys)
        if left_sibling != None: # merge with left sibling
            if node.leaf == True:
                left_sibling.keys.extend(node.keys)
                left_sibling.pointers.extend(node.pointers)
                left_sibling.next = node.next
            else:
                left_sibling.keys.append(parent.keys[index - 1])
                left_sibling.keys.extend(node.keys)
                left_sibling.children.extend(node.children)
            parent.keys.pop(index - 1)
            parent.children.pop(index)
        elif right_sibling != None: # merge with right sibling
            if node.leaf == True:
                node.keys.extend(right_sibling.keys)
                node.pointers.extend(right_sibling.pointers)
                node.next = right_sibling.next
            else:
                node.keys.append(parent.keys[index])
                node.keys.extend(right_sibling.keys)
                node.children.extend(right_sibling.children)
            parent.keys.pop(index)
            parent.children.pop(index + 1)
        self.satisfy_properties(parent, path, index_list)

    def key_delete(self, deleting_key):
        location, path, index_list = self.where_to_insert(deleting_key)
        pointer = self.search(self.root, deleting_key)[0]
        if pointer == None:
            return None
        
        for i in range(len(location.keys)):
            if location.keys[i] == deleting_key:
                index = i
                break
        location.keys.pop(index)
        location.pointers.pop(index)
        self.satisfy_properties(location, path, index_list)

        # update student_info
        last_index = len(student_info) - 1
        if pointer < last_index:
            last_student_id = int(student_info[-1]['Student ID'])
            student_info[pointer] = student_info[-1]
            self.change_pointer(self.root, last_student_id, pointer)
        student_info.pop()

        return pointer

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
    
 # ============================================
 # B*-tree
 # ============================================

class Bstar_tree_node:
    def __init__(self, leaf = False):
        self.leaf = leaf
        self.keys = []
        self.pointers = []
        self.children = []
class Bstar_tree:
    def __init__(self, order):
        self.root = Bstar_tree_node(leaf = True)
        self.order = order

    def search(self, node, searching_key):
        i = 0
        while (i < len(node.keys)) and (searching_key > node.keys[i]):
            i += 1
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                return node.pointers[i], node
        if node.leaf == True:
            return None, None
        else:
            return self.search(node.children[i], searching_key)
        
    def change_pointer(self, node, searching_key, new_pointer):
        i = 0
        while (i < len(node.keys)) and (searching_key > node.keys[i]):
            i += 1
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                node.pointers[i] = new_pointer
                return True
        if node.leaf == True:
            return False
        else:
            return self.change_pointer(node.children[i], searching_key, new_pointer)
        
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
    
    # merge two nodes and split into three nodes
    def merge2_split3(self, first_node, second_node, parent, index):
        all_keys = first_node.keys + [parent.keys[index]] + second_node.keys
        all_pointers = first_node.pointers + [parent.pointers[index]] + second_node.pointers
        if first_node.leaf == False:
            all_children = first_node.children + second_node.children
        else:
            all_children = []

        number_of_all_keys = len(all_keys)
        first_node_size = number_of_all_keys // 3
        second_node_size = number_of_all_keys // 3
        if number_of_all_keys % 3 == 0:
            first_node_size -= 1
            second_node_size -= 1
        elif number_of_all_keys % 3 == 1:
            first_node_size -= 1
            
        third_node = Bstar_tree_node(leaf = first_node.leaf)
        # split to three nodes
        first_node.keys = all_keys[:first_node_size]
        first_node.pointers = all_pointers[:first_node_size]
        second_node.keys = all_keys[first_node_size + 1:first_node_size + second_node_size + 1]
        second_node.pointers = all_pointers[first_node_size + 1:first_node_size + second_node_size + 1]
        third_node.keys = all_keys[first_node_size + second_node_size + 2:]
        third_node.pointers = all_pointers[first_node_size + second_node_size + 2:]
        if first_node.leaf == False: # if not leaf node, split children as well
            first_node.children = all_children[:first_node_size + 1]
            second_node.children = all_children[first_node_size + 1:first_node_size + second_node_size + 2]
            third_node.children = all_children[first_node_size + second_node_size + 2:]

        parent.keys[index] = all_keys[first_node_size]
        parent.pointers[index] = all_pointers[first_node_size]
        parent.keys.insert(index + 1, all_keys[first_node_size + second_node_size + 1])
        parent.pointers.insert(index + 1, all_pointers[first_node_size + second_node_size + 1])
        parent.children.insert(index + 2, third_node)
    
    def key_insert(self, inserting_key, pointer):
        location, path, index_list = self.where_to_insert(inserting_key)
        i = 0
        while ((i < len(location.keys)) and (location.keys[i] < inserting_key)):
            i += 1
        location.keys.insert(i, inserting_key)
        location.pointers.insert(i, pointer)

        while len(location.keys) >= self.order: # node redistribution or split
            
            if len(path) == 0: # root node
                mid = len(location.keys) // 2
                mid_key = location.keys[mid]
                mid_pointer = location.pointers[mid]
                right = Bstar_tree_node(leaf = location.leaf)
                right.keys = location.keys[mid+1:]
                right.pointers = location.pointers[mid+1:]
                location.keys = location.keys[:mid]
                location.pointers = location.pointers[:mid]
                if location.leaf == False:
                    right.children = location.children[mid+1:]
                    location.children = location.children[:mid+1]
                new_root = Bstar_tree_node(leaf = False)
                new_root.keys.append(mid_key)
                new_root.pointers.append(mid_pointer)
                new_root.children.append(location)
                new_root.children.append(right)
                self.root = new_root
                return
            
            parent = path.pop()
            index = index_list.pop()
            
            if index == 0:
                left_sibling = None
                right_sibling = parent.children[index + 1]
            elif index == len(parent.children) - 1:
                left_sibling = parent.children[index - 1]
                right_sibling = None
            else:
                left_sibling = parent.children[index - 1]
                right_sibling = parent.children[index + 1]
            
            # distribution (distribute to sibling that has less keys)
            to_left = False
            to_right = False
            if left_sibling == None:
                if len(right_sibling.keys) < self.order - 1:
                    to_right = True
            elif right_sibling == None:
                if len(left_sibling.keys) < self.order - 1:
                    to_left = True
            else:
                if len(left_sibling.keys) > len(right_sibling.keys):
                    to_right = True
                elif len(left_sibling.keys) < self.order - 1:
                    to_left = True
            # distribute to left
            if to_left == True:
                left_sibling.keys.append(parent.keys[index - 1])
                left_sibling.pointers.append(parent.pointers[index - 1])
                if location.leaf == False:
                    left_sibling.children.append(location.children.pop(0))         
                parent.keys[index - 1] = location.keys.pop(0)
                parent.pointers[index - 1] = location.pointers.pop(0)
                return

            # distribute to right
            if to_right == True:
                right_sibling.keys.insert(0, parent.keys[index])
                right_sibling.pointers.insert(0, parent.pointers[index])
                if location.leaf == False:
                    right_sibling.children.insert(0, location.children.pop())  
                parent.keys[index] = location.keys.pop()
                parent.pointers[index] = location.pointers.pop()
                return

            # merge and split (if both siblings have maximum number of keys)
            if left_sibling != None:
                self.merge2_split3(left_sibling, location, parent, index - 1)
            elif right_sibling != None:
                self.merge2_split3(location, right_sibling, parent, index)
            location = parent

    def where_to_delete(self, node, searching_key, path, index_list):
        i = 0
        while (i < len(node.keys)) and (searching_key > node.keys[i]):
            i += 1
        if i < len(node.keys):
            if node.keys[i] == searching_key:
                return node.pointers[i], node
        if node.leaf == True:
            return None, None
        else:
            path.append(node)
            index_list.append(i)
            return self.where_to_delete(node.children[i], searching_key, path, index_list)

    def satisfy_properties(self, node, path, index_list):
        min_keys = math.ceil(2 * self.order / 3) - 1
        # eception for root node with only two children
        if len(path) == 1:
            if len(path[0].children) == 2:
                min_keys = math.ceil(self.order / 2) - 1

        if len(path) == 0: # root node
            if len(node.keys) == 0:
                if len(node.children) > 0:
                    self.root = node.children[0]
            return
        if len(node.keys) >= min_keys: # tree satisfy the properties
            return

        parent = path.pop()
        index = index_list.pop()
        if index == 0:
            left_sibling = None
            right_sibling = parent.children[index + 1]
        elif index == len(parent.children) - 1:
            left_sibling = parent.children[index - 1]
            right_sibling = None
        else:
            left_sibling = parent.children[index - 1]
            right_sibling = parent.children[index + 1]

        # Borrow from sibling that has more keys
        from_left = True
        if (left_sibling != None) and (len(left_sibling.keys) > min_keys) and (right_sibling != None) and (len(right_sibling.keys) > min_keys):
            if len(left_sibling.keys) < len(right_sibling.keys):
                from_left = False
        # Borrow from left sibling
        if (left_sibling != None) and (len(left_sibling.keys) > min_keys) and (from_left == True):
            node.keys.insert(0, parent.keys[index - 1])
            node.pointers.insert(0, parent.pointers[index - 1])
            if node.leaf == False:
                node.children.insert(0, left_sibling.children.pop())
            parent.keys[index - 1] = left_sibling.keys.pop()
            parent.pointers[index - 1] = left_sibling.pointers.pop()
            return
        # Borrow from right sibling
        if (right_sibling != None) and (len(right_sibling.keys) > min_keys):
            node.keys.append(parent.keys[index])
            node.pointers.append(parent.pointers[index])
            if node.leaf == False:
                node.children.append(right_sibling.children.pop(0))
            parent.keys[index] = right_sibling.keys.pop(0)
            parent.pointers[index] = right_sibling.pointers.pop(0)
            return

        # merge (if both siblings have only minimum number of keys)
        if len(parent.children) >= 3:
            if (left_sibling != None) and (right_sibling != None): # both siblings exist
                self.merge3_split2(left_sibling, node, right_sibling, parent, index - 1)
            elif index == 0: # only right sibling exist
                right_right_sibling = parent.children[index + 2]
                self.merge3_split2(node, right_sibling, right_right_sibling, parent, index)
            else: # only left sibling exist
                left_left_sibling = parent.children[index - 2]
                self.merge3_split2(left_left_sibling, left_sibling, node, parent, index - 2)
        else: # root node has only two children
            if left_sibling != None:
                left_sibling.keys.append(parent.keys.pop(index - 1))
                left_sibling.pointers.append(parent.pointers.pop(index - 1))
                left_sibling.keys.extend(node.keys)
                left_sibling.pointers.extend(node.pointers)
                if node.leaf == False:
                    left_sibling.children.extend(node.children)
                parent.children.pop(index)
            else:
                node.keys.append(parent.keys.pop(index))
                node.pointers.append(parent.pointers.pop(index))
                node.keys.extend(right_sibling.keys)
                node.pointers.extend(right_sibling.pointers)
                if node.leaf == False:
                    node.children.extend(right_sibling.children)
                parent.children.pop(index + 1)

        self.satisfy_properties(parent, path, index_list)

    # merge three nodes and split into two nodes
    def merge3_split2(self, first_node, second_node, third_node, parent, index):
        all_keys = first_node.keys + [parent.keys[index]] + second_node.keys + [parent.keys[index + 1]] + third_node.keys
        all_pointers = first_node.pointers + [parent.pointers[index]] + second_node.pointers + [parent.pointers[index + 1]] + third_node.pointers
        
        if first_node.leaf == False:
            all_children = first_node.children + second_node.children + third_node.children
        else:
            all_children = []
        
        mid = len(all_keys) // 2
        # split to two nodes
        first_node.keys = all_keys[:mid]
        first_node.pointers = all_pointers[:mid]
        second_node.keys = all_keys[mid + 1:]
        second_node.pointers = all_pointers[mid + 1:]
        if first_node.leaf == False: # if not leaf node, split children as well
            first_node.children = all_children[:mid + 1]
            second_node.children = all_children[mid + 1:]

        parent.keys.pop(index + 1)
        parent.pointers.pop(index + 1)
        parent.children.pop(index + 2)
        parent.keys[index] = all_keys[mid]
        parent.pointers[index] = all_pointers[mid]
    
    def key_delete(self, deleting_key):
        path = []
        index_list = []
        pointer, delete_node = self.where_to_delete(self.root, deleting_key, path, index_list)
        if pointer == None:
            return None
        elif delete_node.leaf == False:
            for i in range(len(delete_node.keys)):
                if delete_node.keys[i] == deleting_key:
                    path.append(delete_node)
                    index_list.append(i+1)
                    current_node = delete_node.children[i+1]
                    break
            while current_node.leaf == False:
                path.append(current_node)
                index_list.append(0)
                current_node = current_node.children[0]
            successor_key = current_node.keys[0]
            successor_pointer = current_node.pointers[0]
            for i in range(len(delete_node.keys)):
                if delete_node.keys[i] == deleting_key:
                    delete_node.keys[i] = successor_key
                    delete_node.pointers[i] = successor_pointer
                    break
            final_delete_node = current_node
            index_to_delete = 0
        else:
            for i in range(len(delete_node.keys)):
                if delete_node.keys[i] == deleting_key:
                    break
            final_delete_node = delete_node
            index_to_delete = i
        final_delete_node.keys.pop(index_to_delete)
        final_delete_node.pointers.pop(index_to_delete)

        self.satisfy_properties(final_delete_node, path, index_list)

        # update student_info
        last_index = len(student_info) - 1
        if pointer < last_index:
            last_student_id = int(student_info[-1]['Student ID'])
            student_info[pointer] = student_info[-1]
            self.change_pointer(self.root, last_student_id, pointer)
        student_info.pop()

        return pointer

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

 # ==========================================
 # Selecting tree type and fanout order, and measuring insertion time
 # ========================================== 
tree_type = '0'
fanout_order = 0
while tree_type != '1' and tree_type != '2' and tree_type != '3':
    tree_type = input("which type of tree? (1: B-tree, 2: B+-tree, 3: B*-tree): ")
while fanout_order < 2:
    fanout_order = int(input("fanout order of tree: "))
    if fanout_order < 2:
        print("fanout order should be larger than 2.")
if tree_type == '1': # B-tree
    tree = Btree(order = fanout_order)
elif tree_type == '2': # B+-tree
    tree = Bplus_tree(order = fanout_order)
elif tree_type == '3': # B*-tree
    tree = Bstar_tree(order = fanout_order)
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
        result = tree.search(tree.root, int(target_id))[0]
        if result != None:
            student_data = student_info[result]
            print(f"data: {student_data}")
        else:
            print("there is no student with that ID.")
    elif operation == '2': # insert
        data = input("which student data to insert (format: Student ID, Name, Gender, GPA, Height, Weight): ")
        split_data= data.split(', ')
        if len(split_data) == 6:
            student_id, name, gender, gpa, height, weight = split_data
            student_info.append({'Student ID': student_id, 'Name': name, 'Gender': gender, 'GPA': gpa, 'Height': height, 'Weight': weight})
            tree.key_insert(int(student_id), len(student_info) - 1)
        else:
            print("invalid data format.")
    elif operation == '3': # delete
        if len(student_info) > 0:
            delete_id = input("which student ID to delete: ")
            result = tree.key_delete(int(delete_id))
            if result == None:
                print("there is no student with that ID.")
        else:
            print("tree is empty.")
    elif operation == '4': # others
        detail_operation = input("which operation? (1: point search, 2: range query, 3: delete multiple IDs): ")
        if detail_operation == '1': # point search
            num = int(input("how many point searches? "))
            if num <= len(student_info):
                student_ids = [student['Student ID'] for student in student_info]
                search_ids = random.sample(student_ids, num)
                deleted_id = 0
                start_time = time.perf_counter()
                for search_id in search_ids:
                    if search_id != None:
                        tree.search(tree.root, int(search_id))
                    else:
                        deleted_id += 1
                end_time = time.perf_counter()
                if deleted_id > 0:
                    print(f"{deleted_id} IDs are already deleted. So failed to search those IDs.")
                print(f"total time: {end_time - start_time:.6f} seconds.")
                print(f"mean time: {(end_time - start_time) / num:.8f} seconds.")
            else:
                print(f"there are only {len(student_info)} students.")
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
        elif detail_operation == '3': # delete multiple IDs
            if len(student_info) > 0:
                want_to_delete = int(input("how many keys to delete?: "))
                if len(student_info) < want_to_delete:
                    how_many = len(student_info)
                else:
                    how_many = want_to_delete
                student_ids = [student['Student ID'] for student in student_info]
                delete_ids = random.sample(student_ids, how_many)
                start_time = time.perf_counter()
                for delete_id in delete_ids:
                    if delete_id != None:
                        result = tree.key_delete(int(delete_id))
                end_time = time.perf_counter()
                print(f"total time for deletion: {end_time - start_time:.6f} seconds.")
                if how_many == want_to_delete:
                    print(f"{how_many} keys are deleted.\nremaining keys: {len(student_info)}")
                else:
                    print(f"there are only {how_many} keys. Therefore, all keys are deleted.")
            else:
                print("tree is empty.")
    operation = input("which operation? (1: search, 2: insert, 3: delete, 4: others, 5: exit): ")
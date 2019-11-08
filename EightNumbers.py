"""
Created on Mar 27, 2019

@author: neal
"""
import numpy as np
import sortedcontainers
from math import factorial


class AStarForEightNumbers:
    def __init__(self, start, end):
        self.n = len(start)
        self.check_input(start, end)
        self.start = self.transform(start)
        self.end = self.transform(end)

        self.open = sortedcontainers.SortedList([])
        self.factorial = [factorial(i) for i in range(self.n * self.n)]
        self.find_deep = [-1] * self.factorial[-1]
        self.find_parent = [-1] * self.factorial[-1]
        self.search_count = 0

        self.cantor_start = self.cantor(self.start)
        self.cantor_end = self.cantor(self.end)

        # note that we do not need a close list

    class Node:
        """
        to store a search result
        """

        def __init__(self, cantor_idx, cost):
            """
            initialization
            :param cantor_idx: int
            :param cost: float
            """
            self.cantor_idx = cantor_idx
            self.cost = cost

        def __lt__(self, other):
            """
            write the compare method
            :param other: Node
            :return: bool
            """
            return self.cost > other.cost

    def solution(self):
        """
        the main function to solve the problem
        :return: None
        """
        # check if the solution exists
        if not self.have_solution():
            print("No result.")
            return

        current = self.Node(self.cantor_start, self.get_cost(self.start))
        self.find_deep[self.cantor_start] = 0

        while current.cantor_idx != self.cantor_end:
            self.extension(current)
            current = self.open.pop()
            self.search_count += 1

        self.print_result(current)

    def extension(self, parent):
        """
        extend the parent Node
        :param parent: Node
        :return: None
        """
        state = self.decantor(parent.cantor_idx)

        position = np.argmin(state)

        # try four directions
        if position // self.n != 0:
            temp = state.copy()
            temp[position] = temp[position - self.n]
            temp[position - self.n] = 0
            self.update_open(temp, parent)

        if position // self.n != self.n - 1:
            temp = state.copy()
            temp[position] = temp[position + self.n]
            temp[position + self.n] = 0
            self.update_open(temp, parent)

        if position % self.n != 0:
            temp = state.copy()
            temp[position] = temp[position - 1]
            temp[position - 1] = 0
            self.update_open(temp, parent)

        if position % self.n != self.n - 1:
            temp = state.copy()
            temp[position] = temp[position + 1]
            temp[position + 1] = 0
            self.update_open(temp, parent)

    def update_open(self, temp, parent):
        """
        check if temp have appeared. if so, update open
        :param temp: Node
        :param parent: Node
        :return: None
        """
        cantor_idx = self.cantor(temp)

        if self.find_deep[cantor_idx] == -1:
            self.find_deep[cantor_idx] = self.find_deep[parent.cantor_idx] + 1
            self.find_parent[cantor_idx] = parent.cantor_idx
            temp_cost = self.find_deep[parent.cantor_idx] + 1 + self.get_cost(temp)
            node_temp = self.Node(cantor_idx, temp_cost)
            self.open.add(node_temp)

        # if temp have appeared, but the deep here is smaller, update.
        elif self.find_deep[cantor_idx] > self.find_deep[parent.cantor_idx] + 1:
            self.find_deep[cantor_idx] = self.find_deep[parent.cantor_idx] + 1
            self.find_parent[cantor_idx] = parent.cantor_idx

    def print_result(self, end):
        """
        print the result
        :param end: Node
        :return: None
        """
        cantor_idx = end.cantor_idx
        result = [self.decantor(cantor_idx)]

        while self.find_parent[cantor_idx] != -1:
            result.append(self.decantor(self.find_parent[cantor_idx]))
            cantor_idx = self.find_parent[cantor_idx]

        result.reverse()
        for i, state in enumerate(result):
            if i:
                print(f"the {i}-th step is: ")
            else:
                print("the original situation is: ")
            print(np.array(state).reshape(3, 3))

        step_number = len(result) - 1
        print(f"That is what we want. \nThe total number of steps is {step_number}.")
        print(f"Total number of searches is {self.search_count}")

    def have_solution(self):
        """
        check if any solution exists using inversion
        :return: bool
        """
        start_inversion = 0
        end_inversion = 0
        for i in range(self.n * self.n):
            for j in range(i):
                if self.start[i] < self.start[j] and self.start[i]:
                    start_inversion += 1
                if self.end[i] < self.end[j] and self.end[i]:
                    end_inversion += 1

        if self.n % 2 == 1:
            return start_inversion % 2 == end_inversion % 2
        else:
            start_zero_position = np.argmin(self.start)
            end_zero_position = np.argmin(self.end)
            h_distance = abs(start_zero_position // self.n - end_zero_position // self.n)
            return (start_inversion + h_distance) % 2 == end_inversion % 2

    def get_cost(self, state):
        """
        calculate the estimated distance between state and the destination
        :param state: Node
        :return: float
        """
        result = 0
        for i in range(self.n * self.n):
            for j in range(self.n * self.n):
                if state[i] == self.end[j]:
                    result += (abs(i // self.n - j // self.n) + abs(i % self.n - j % self.n)) * (state[i])
                    # 这里采用了每个数字回到目标位置的最小步数乘以数字作为权重的求和
                    # 这是因为，我们希望计算机优先复原某几个数字，而不是均等对待
                    # 实证表明这样比单纯求和效率高
        return result

    def cantor(self, state):
        """
        calculate the cantor expansion of the given state
        :param state:
        :return: int
        """
        result = 0
        for i in range(self.n * self.n):
            count = 0
            for j in range(i, self.n * self.n):
                if state[i] > state[j]:
                    count += 1
            result += count * self.factorial[self.n * self.n - i - 1]
        return result

    def decantor(self, cantor_idx):
        """
        calculate the decantor expansion of the given cantor_idx
        :param cantor_idx: int
        :return: array-like, len = self.n * self.n
        """
        number = list(range(self.n * self.n))
        result = [0] * (self.n * self.n)
        for i in range(self.n * self.n):
            t = cantor_idx // self.factorial[self.n * self.n - i - 1]
            cantor_idx %= self.factorial[self.n * self.n - i - 1]
            result[i] = number[t]
            number.pop(t)
        return np.array(result)

    def check_input(self, start, end):
        """
        check if the input is (3, 3), and composite by range(9)
        :param start: list, shape = (3, 3)
        :param end: list, shape = (3, 3)
        :return: None
        """
        array_start = np.array(start)
        if array_start.shape != (self.n, self.n) or set(array_start.ravel()) != set(range(self.n * self.n)):
            raise ValueError("The input is illegal!")

        array_end = np.array(end)
        if array_end.shape != (self.n, self.n) or set(array_end.ravel()) != set(range(self.n * self.n)):
            raise ValueError("The input is illegal!")

    def transform(self, state):
        """
        transform the given state into a one dimensional list
        :param state: list, shape = (self.n, self.n)
        :return: array-like, len = self.n * self.n
        """
        return np.array(state).ravel()


if __name__ == '__main__':
    # test
    test_start = [[1, 0, 4],
                  [7, 3, 5],
                  [8, 6, 2]
                  ]

    test_end = [[1, 3, 2],
                [7, 0, 4],
                [6, 5, 8]
                ]

    AStarForEightNumbers(test_start, test_end).solution()

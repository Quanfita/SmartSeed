# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 18:13:22 2019

@author: Quanfita
"""

class OpStack(object):
    def __init__(self):
        self.stack=[]
    def isEmpty(self):
        return self.stack==[]
    def push(self,item):
        self.stack.append(item)
    def pop(self):
        if self.isEmpty():
            raise IndexError('pop from empty stack')
        return self.stack.pop()
    def peek(self):
        return self.stack[-1]
    def size(self):
        return len(self.stack)
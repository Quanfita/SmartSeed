# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 18:13:22 2019

@author: Quanfita
"""

class OpStack(object):
    def __init__(self):
        self.stack=[]
        self.restack = []
        
    def isEmpty(self):
        if self.stack:
            return False
        return True
    
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
    
    def re_size(self):
        return len(self.restack)
    
    def re_isEmpty(self):
        if self.restack:
            return False
        return True
    
    def re_pop(self):
        if self.re_isEmpty():
            return
        return self.restack.pop()
    
    def re_peek(self):
        return self.restack[-1]
    
    def re_push(self,item):
        self.restack.append(item)
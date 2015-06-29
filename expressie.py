import math

#list with information about operators and their properties
oplist = ['+','-','*','/','**']
preclist={'+':2, '-':2, '*':3, '/':3, '**':4}
left_assoclist={'+':True,'-':True,'*':True,'/':True,'**':False}
right_assoclist={'+':True,'-':False,'*':True,'/':False,'**':True}
printoptie = 'normal'

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces
def tokenize(string):
    splitchars = list("+-*/(),")
    
    # surround any splitchar by spaces
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)
    tokenstring = ''.join(tokenstring)
    #split on spaces - this gives us our tokens
    tokens = tokenstring.split()
    #special casing for **:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans
    
# check if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# check if a string represents an integer value        
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
        
# check if a string represents a variable
def isvar(string):
    try:
        Variable(string)
        Value = True and not isnumber(string) and not string in ['+', '-', '*', '/', '**','(',')']
        return Value
    except ValueError:
        return False
        
class Expression():
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
     - evaluate_node(self,dic={}: to calculate the outcome of an expression, given the values of variables in dictionary
     - derivative(self, variable): return the derivative of the expression
     - primitive(self, variable): return primitive of the expression
    """
    #evaluate, derivative, primitive recursive defined
    
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)
    def __sub__(self, other):
        return SubNode(self, other)
    def __mul__(self,other):
        return MulNode(self,other)
    def __truediv__(self,other):
        return DivNode(self,other)
    def __pow__(self,other):
        return ExpNode(self,other)
    
    #Shunting-yard algorithm
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        output = []
        
        for token in tokens:
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
            elif isvar(token): 
                # variables go directly to output as well
                output.append(Variable(token))
            elif token in oplist:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    if len(stack) == 0 or stack[-1] not in oplist:
                        break
                    if (left_assoclist[token]==True and preclist[token]<=preclist[stack[-1]]) or (left_assoclist[token]==False and preclist[token]<preclist[stack[-1]]):
                        output.append(stack.pop())
                    else:
                        break
                # push the new operator onto the stack
                stack.append(token)
            elif token == '(':
                # left parantheses go to the stack
                stack.append(token)
            elif token == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] == '(':     
                    output.append(stack.pop())
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()
            else:
                raise ValueError('Unknown token: %s' % token)
            
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            else:
                # a constant or variable, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        
        return stack[0]

# evaluate takes care of regulating if you need partial evaluation or full evaluation
def evaluate(expression,dic = {}):
    try:
        float(expression.evaluate_node(dic))
        return expression.evaluate_node(dic)
        
    except ValueError:
        return PartialEvaluation(expression,dic)


class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value, prec=1000):
        self.value = value
        self.prec = 1000
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    def normal(self):
        return str(self.value)
    
    def tree(self):
        return str(self.value)
        
    def simplify(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
    
    def evaluate_node(self,dic={}):
        return self.value
    
    def derivative(self, variable = 'Object'): #derivative of constant is 0
        return Constant(0)
        
    def primitive(self, variable):
        return self*Variable(variable)
        
class Variable(Expression):
    """Represents a variable"""
    
    def __init__(self, symb, prec=1000):
        self.symb = symb
        self.prec = 1000
        
    def __str__(self):
        return self.symb
        
    def normal(self):
        return self.symb
        
    def tree(self):
        return self.symb
        
    def simplify(self):
        return self.symb
        
    def __eq__(self,other):
        if isinstance(other, Variable):
            return self.symb == other.symb
        else:
            return False
            
    def evaluate_node(self,dic={}): 
        if self.symb in dic:
            return dic[self.symb]
        else:
            return self.symb
            
    def derivative(self, variable = 'Object'):
        if variable == 'Object':
            return self.derivative(self.symb)
        else:
            if self.symb == variable: #here is a notion of partial differential evaluation, if the given variable is x,  y'=0
                return Constant(1)
            else:
                return Constant(0)
    def primitive(self,variable):
        if self.symb == variable:
            return Constant(0.5)*Variable(variable)**Constant(2)
        else:
            return Variable(variable)

class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol, prec, assoc_left,assoc_right):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        self.prec = prec
        self.assoc_left = assoc_left 
        self.assoc_right = assoc_right
        
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False

#check which printoption is asked            
    def __str__(self):
        if printoptie == 'normal':
            return self.normal()
        elif printoptie == 'tree':
            return self.tree()
        elif printoptie == 'simplify':
            return self.simplify()

    #print the expression only with parantheses that are necessary, conventional notation    
    def normal(self):    

        lstring = self.lhs.normal()
        rstring = self.rhs.normal()
        
        if (self.lhs.prec<self.prec) or (self.lhs.prec==self.prec and not self.assoc_left):
            #put parantheses on leftside, as in tree ((5*2)**5), 5*2 needs parantheses, 
            #((3**4)**5) then prec=left_prec but left not left associative so 3**4 needs parantheses
            lstring = '('+lstring+')' #dit zorgt voor haakjes om lstring
        if (self.rhs.prec<self.prec) or (self.rhs.prec==self.prec and not self.assoc_right):
            #put parantheses on right side, as in tree (3*(2+3)), 2+3 needs parantheses, 
            #(2-(5-8)) then prec=right_prec but right not right associative so 5-8 needs parantheses
            rstring = '('+rstring+')' #dit zorgt voor haakjes om rstring
    
        return "%s %s %s" % (lstring, self.op_symbol, rstring)
    
    #print with parantheses around every part of the expression that represents a node   
    def tree(self):
        
        lstring = self.lhs.tree()
        rstring = self.rhs.tree()
        
        return "(%s %s %s)" % (lstring, self.op_symbol, rstring)
    
    #print without unnecessary parts of the expression +0, *0, *1    
    def simplify(self):
        
        lstring = self.lhs.simplify()
        rstring = self.rhs.simplify()
        

        if self.op_symbol == '+':
            if self.lhs == Constant(0):
                 self.prec = self.rhs.prec 
                 return self.rhs.simplify()
            elif self.rhs == Constant(0):
                 self.prec = self.lhs.prec
                 return self.lhs.simplify()
            
        elif self.op_symbol == '*':
            if self.lhs == Constant(0) or self.rhs == Constant(0):
                return str(Constant(0))
            if self.lhs == Constant(1) or lstring == str(1): 
                return self.rhs.simplify()
            elif self.rhs == Constant(1) or rstring == str(1): 
                return self.rhs.simplify()
        elif self.op_symbol == '/':
            if self.lhs == Constant(0) or lstring == str(0) and self.rhs != str(0):
                return str(Constant(0))
            if self.rhs == Constant(1) or rstring == str(1):
                return self.lhs.simplify()
            if self.lhs == self.rhs and self.rhs != Constant(0):
                return str(Constant(1))
                
        if (self.lhs.prec<self.prec) or (self.lhs.prec==self.prec and not self.assoc_left):
            #put parantheses on leftside, as in tree ((5*2)**5), 5*2 needs parantheses, 
            #((3**4)**5) then prec=left_prec but left not left associative so 3**4 needs parantheses
            lstring = '('+lstring+')' #dit zorgt voor haakjes om lstring
        if (self.rhs.prec<self.prec) or (self.rhs.prec==self.prec and not self.assoc_right):
            #put parantheses on right side, as in tree (3*(2+3)), 2+3 needs parantheses, 
            #(2-(5-8)) then prec=right_prec but right not right associative so 5-8 needs parantheses
            rstring = '('+rstring+')' #dit zorgt voor haakjes om rstring
        
        return "%s %s %s" % (lstring, self.op_symbol, rstring)            
            

class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+',preclist['+'],left_assoclist['+'],right_assoclist['+'])
        
    def evaluate_node(self, dic={}): 
        if not (isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str)): 
            return self.lhs.evaluate_node(dic)+self.rhs.evaluate_node(dic) # spreekt redelijk voor zich lijkt me
    
        elif isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str): # dit zorgt voor partial evaluate_node
            return "(%s) %s (%s)" % (self.lhs.evaluate_node(dic), self.op_symbol, self.rhs.evaluate_node(dic))
        
    def derivative(self,variable='Object'):
        return self.lhs.derivative(variable)+self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        return self.lhs.primitive(variable)+self.rhs.primitive(variable)
    
    
class SubNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(SubNode,self).__init__(lhs, rhs, '-',preclist['-'],left_assoclist['-'],right_assoclist['-'])
        
    def evaluate_node(self, dic={}): 
        if not (isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str)): 
            return self.lhs.evaluate_node(dic)-self.rhs.evaluate_node(dic)       
    
        elif isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate_node(dic), self.op_symbol, self.rhs.evaluate_node(dic))
        
    def derivative(self,variable='Object'):
        return self.lhs.derivative(variable)-self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        return self.lhs.primitive(variable)-self.rhs.primitive(variable)        
class MulNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(MulNode,self).__init__(lhs, rhs, '*',preclist['*'],left_assoclist['*'],right_assoclist['*'])
        
    def evaluate_node(self, dic={}): 
        if not (isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str)): 
            return self.lhs.evaluate_node(dic)*self.rhs.evaluate_node(dic)       
    
        elif isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate_node(dic), self.op_symbol, self.rhs.evaluate_node(dic))
        
    def derivative(self,variable='Object'):
        return self.lhs.derivative(variable)*self.rhs+self.lhs*self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        if type(self.lhs) == Constant:
            return self.lhs*self.rhs.primitive(variable)
            
        elif type(self.rhs) == Constant:
            return self.rhs*self.lhs.primitive(variable)
        
        else:
            raise ValueError('Sorry, I can\'t integrate this type of function.')
            
class DivNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(DivNode,self).__init__(lhs, rhs, '/',preclist['/'],left_assoclist['/'],right_assoclist['/'])

    def evaluate_node(self, dic={}): 
        if not (isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str)): 
            return self.lhs.evaluate_node(dic)/self.rhs.evaluate_node(dic)       
    
        elif isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate_node(dic), self.op_symbol, self.rhs.evaluate_node(dic))
        
        
    def derivative(self,variable='Object'):
        return (self.lhs.derivative(variable)*self.rhs-self.lhs*self.rhs.derivative(variable))/(self.rhs*self.rhs) 
    
    def primitive(self,variable):
        if type(self.lhs) == Constant and type(self.rhs) == Constant:
            return self*Variable(variable)
        elif type(self.lhs) == Variable and type(self.rhs) == Constant:
            return Constant(0.5)*self.rhs*Variable(variable)**2
        else:    
            raise ValueError('Sorry, I can\'t integrate this type of function.')
        
class ExpNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(ExpNode,self).__init__(lhs, rhs, '**',preclist['**'],left_assoclist['**'],right_assoclist['**'])
        
    def evaluate_node(self, dic={}): 
        if not (isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str)): 
            return self.lhs.evaluate_node(dic)**self.rhs.evaluate_node(dic)       
    
        elif isinstance(self.lhs.evaluate_node(dic),str) or isinstance(self.rhs.evaluate_node(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate_node(dic), self.op_symbol, self.rhs.evaluate_node(dic))
    
    def derivative(self,variable):
        if type(self.lhs) == Variable and type(self.rhs) == Constant:
            return self.rhs*(self.lhs**(self.rhs-Constant(1)))
        if type(self.lhs) == Constant and type(self.rhs) == Variable:
            return Constant(math.log(self.lhs.value))*self
        else:
            raise ValueError('Sorry, We did not add the logarithm function so we can not differentiate this.')
        
        
    def primitive(self,variable):
        if type(self.rhs) == Constant and type(self.lhs) == Variable:
            return (Constant(1)/(self.rhs+Constant(1)))*Variable(variable)*self
        if type(self.lhs) == Constant and type(self.rhs) == Variable:
            return (Constant(1)/Constant(math.log(self.lhs.value)))*self
        if type(self.lhs) == Constant and type(self.rhs) == Constant:
            return self*Variable(variable)
        else:
            raise ValueError('Sorry, I can\'t integrate this type of function.')
            
#numerical integration
def NumInt(function,variable,leftinterval,rightinterval,step): 
    FirstInterval = leftinterval+0.5*step
    Evaluation = [function.evaluate_node({variable:FirstInterval})]
    i = step
    while i+FirstInterval<=rightinterval:
        Evaluation.append(function.evaluate_node({variable:i+FirstInterval}))
        i=i+step
    return sum(Evaluation)*(FirstInterval-leftinterval)*2
    
#numerical test of the fundamental Theorem of Calculus
def TestFundThmOfCalculus(function,variable): 
    Function = function.primitive(variable)
    LeftValue = Function.evaluate_node({variable:1})
    RightValue = Function.evaluate_node({variable:4})
    Distance = RightValue - LeftValue
    RiemannSum = NumInt(function,'x',1,4,0.0001)
    if abs(Distance-RiemannSum)<0.01:
        return 'The fundamental theorem of calculus is propably true (checked numerically).'
    else:
        return 'It seems that the fundamental theorem of calculus is false (that seems strange since it has already been proven)'
        
def PartialEvaluation(Expr, dic):
    return Expression.fromString(Expr.evaluate_node(dic))
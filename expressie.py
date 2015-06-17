import math

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

class Expression():
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
    """
    # TODO: when adding new methods that should be supported by all subclasses, add them to this list
    
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)
    def __sub__(self, other):
        return SubNode(self, other)
    def __mul__(self,other):
        return MultNode(self,other)
    def __truediv__(self,other):
        return DivNode(self,other)
    def __pow__(self,other):
        return ExpNode(self,other)
        
    # TODO: other overloads, such as __sub__, __mul__, etc.
    
    # basic Shunting-yard algorithm
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and '+'s
        output = []
        
        # list of operators
        oplist = ['+','-','*','/','**']
        preclist=[2,2,3,3,4]
        assoclist=['L','L','L','L','R']
        
        
        for token in tokens:
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
            elif token in oplist:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    # TODO: when there are more operators, the rules are more complicated
                    # look up the shunting yard-algorithm
                    if len(stack) == 0 or stack[-1] not in oplist: #vanaf hier heb het ik het Shunting-Alg. aangepast (volgens wiki)
                        break
                    z=oplist.index(token)
                    x=oplist.index(stack[-1])
                    if (assoclist[z]=='L' and preclist[z]<=preclist[x]) or (assoclist[z]=='R' and preclist[z]<preclist[x]):
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
            # TODO: do we need more kinds of tokens?
            else:
                # unknown token
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
                # a constant, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        return stack[0]
        
    #is zoiets een goed idee? Het is twaalf uur dus ik moet echt gaan slapen dus tja ik laat het hier maar bij...    
<<<<<<< HEAD
#    def BoomToRPN(expression):
#        stack = []
#        stack.append(expression.op_symbol)
#        if type(expression.lhs) == Constant:
#            stack.append(expression.lhs)
#        if type(expression.lhs) == BinaryNode:
#            BoomToRPN(expression.lhs)
#        if type(expression.rhs) == Constant:
#            stack.append(expression.rhs)
#        if type(expression.rhs) == BinaryNode:
#            BoomToRPN(expression.rhs)
=======
    def BoomToRPN(expression):
        stack = []
        stack.append(expression.op_symbol)
        if type(expression.lhs) == Constant:
            stack.append(expression.lhs)
        if type(expression.lhs) == BinaryNode:
            BoomToRPN(expression.lhs)
        if type(expression.rhs) == Constant:
            stack.append(expression.rhs)
        if type(expression.rhs) == BinaryNode:
            BoomToRPN(expression.rhs)
>>>>>>> 5da3916ca3b2bd680a78217bb715347444755a16
        
        
class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value, prec=1000):
        self.value = value
        self.prec = 1000 #dit heb ik moeten toevoegen, anders snapt __str__ van binarynode constanten niet
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
class Variable(Expression):
    """Represents a variable"""
    
    def __init__(self, symb, prec=1000):
        self.symb = symb
        self.prec = 1000
        
    def __str__(self):
        return self.symb
        
    def __eq__(self,other):
        return self.symb==other.symb
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol, prec, assoc_left,assoc_right):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        self.prec = prec
        self.assoc_left = assoc_left #hier heb ik een nieuw argument toegevoegd
        self.assoc_right = assoc_right #hier heb ik een nieuw argument toegevoegd
        
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        if (self.lhs.prec<self.prec) or (self.lhs.prec==self.prec and not self.lhs.assoc_left):#Doe haakjes om linkerkant immers bij de boom ((5*2)**5) moeten er haakjes om 5*2 in de string
            #als bv ((3**4)**5) dan prec=prec_links maar links is niet linksasso dus doe haakjes om (3**4)
            lstring = '('+lstring+')' #dit zorgt voor haakjes om lstring
        if (self.rhs.prec<self.prec) or (self.rhs.prec==self.prec and not self.rhs.assoc_right):#Doe haakjes om rechterkant immers bij de boom (3*(2+3)) moeten er haakjes om 2+3 in de string
            #als bv (2-(5-8)) dan prec=prec_rechts maar rechts is niet rechtsasso, dus doe haakjes om (5-8)
            rstring = '('+rstring+')' #dit zorgt voor haakjes om rstring
        # TODO: do we always need parantheses?
        return "%s %s %s" % (lstring, self.op_symbol, rstring) #Ik heb hier de haakjes om de %s weggehaald
        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+',2,True,True)
class SubNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(SubNode,self).__init__(lhs,rhs,'-',2,True,False)
class MultNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(MultNode,self).__init__(lhs,rhs,'*',3,True,True)
class DivNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(DivNode,self).__init__(lhs,rhs,'/',3,True,False)
class ExpNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(ExpNode,self).__init__(lhs,rhs,'**',4,False,True)
a=Constant(4)
b=Constant(5)
c=Constant(7)
d=Variable('d')
e=Variable('d')
print(a+b*(c+a))
print((a+b)*(c+a))
print(type(a+b*(c+a)))
expr = Expression.fromString('(4+(5*7))')
print(expr)
# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.
hallo='Dit is raar'
print('Hallo Allemaal (%s)' % hallo)
print(d==e)
#Expression.fromString('1+2*d') #Dit geeft een error waarschijnlijk moeten we iets aan het ShuntingYald Alg. aanpassen

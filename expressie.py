import math
#TODO: dictionary maken van operators en eigenschappenlijstjes

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
# ListOfVariables=[]
def isvar(string):
    try:
        Variable(string)
        Value = True and not isnumber(string) and not string in ['+', '-', '*', '/', '**','(',')'] #and len(list(string)) == 1
        # if Value == True:
        #     ListOfVariables.append(str(Variable(string)))
        return Value
    except ValueError:
        return False

class Expression():
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
     - evaluate(self,dic={}: to calculate the outcome of an expression, given the values of variables in dictionary
     - derivative(self, variable): return the derivative of the expression
     - primitive(self, variable): return primitive of the expression
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
    
    #Shunting-yard algorithm
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
        left_assoclist=[True,True,True,True,False]
        right_assoclist=[True,False,True,False]
        
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
                    z=oplist.index(token)
                    x=oplist.index(stack[-1])
                    if (left_assoclist[z]==True and preclist[z]<=preclist[x]) or (left_assoclist[z]==False and preclist[z]<preclist[x]):
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
                # a constant, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        return stack[0]
        

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
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
    
    def evaluate(self,dic={}):
        return self.value
    
    def derivative(self, variable = 'Matrix'): #afgeleide van constante is 0 #TODO: misschien totale afgeleide toevoegen?
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
        
    def __eq__(self,other):
        if isinstance(other, Variable):
            return self.symb == other.symb
        else:
            return False
            
    def evaluate(self,dic={}): 
        if self.symb in dic:
            return dic[self.symb]
        else:
            return self.symb
            
    def derivative(self, variable = 'Matrix'):
        if variable == 'Matrix':
            return self.derivative(self.symb) # voor nu is dit ok
        else:
            if self.symb == variable: #we voegen hier gelijk een notie van partiele afgeleide in, als we differentieren naar x dan is de afgeleide van y 0
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
        
    
    #TODO: propertie identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        
        
        #simplifier
        if self.op_symbol == '+':
            if self.lhs == Constant(0):
                 self.prec = self.rhs.prec #toegevoegd, ik denk dat het werkt, nog niet uitgebreid getest
                 return str(self.rhs)
            elif self.rhs == Constant(0):
                 self.prec = self.lhs.prec # toegevoegd
                 return str(self.lhs)
            
        elif self.op_symbol == '*':
            if self.lhs == Constant(0) or self.rhs == Constant(0):
                return str(Constant(0))
            if self.lhs == Constant(1) or lstring == str(1): #lstring statement toegevoegd, input in functie gaat niet goed namelijk.
                return str(self.rhs)
            elif self.rhs == Constant(1) or rstring == str(1): #lstring statement toegevoegd, zie boven, ik weet niet of dit de 'mooie oplossing' is? 
            #het deel voor 'or' kan zelfs weg volgens mij, maar dat durf ik niet zomaar te doen ;)
                return str(self.lhs)
                
        if (self.lhs.prec<self.prec) or (self.lhs.prec==self.prec and not self.assoc_left):#Doe haakjes om linkerkant immers bij de boom ((5*2)**5) moeten er haakjes om 5*2 in de string
            #als bv ((3**4)**5) dan prec=prec_links maar links is niet linksasso dus doe haakjes om (3**4)
            lstring = '('+lstring+')' #dit zorgt voor haakjes om lstring
        if (self.rhs.prec<self.prec) or (self.rhs.prec==self.prec and not self.assoc_right):#Doe haakjes om rechterkant immers bij de boom (3*(2+3)) moeten er haakjes om 2+3 in de string
            #als bv (2-(5-8)) dan prec=prec_rechts maar rechts is niet rechtsasso, dus doe haakjes om (5-8)
            rstring = '('+rstring+')' #dit zorgt voor haakjes om rstring
        
        return "%s %s %s" % (lstring, self.op_symbol, rstring)
        
                

class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+',2,True,True)
        
    def evaluate(self, dic={}): 
        if not (isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str)): 
            return self.lhs.evaluate(dic)+self.rhs.evaluate(dic) # spreekt redelijk voor zich lijkt me
    
        elif isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str): # dit zorgt voor partial evaluate
            return "(%s) %s (%s)" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
    def derivative(self,variable='Matrix'):
        return self.lhs.derivative(variable)+self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        return self.lhs.primitive(variable)+self.rhs.primitive(variable)
    
class SubNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(SubNode,self).__init__(lhs,rhs,'-',2,True,False)
        
    def evaluate(self, dic={}): 
        if not (isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str)): 
            return self.lhs.evaluate(dic)-self.rhs.evaluate(dic)       
    
        elif isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
    def derivative(self,variable='Matrix'):
        return self.lhs.derivative(variable)-self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        return self.lhs.primitive(variable)-self.rhs.primitive(variable)        
class MultNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(MultNode,self).__init__(lhs,rhs,'*',3,True,True)
        
    def evaluate(self, dic={}): 
        if not (isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str)): 
            return self.lhs.evaluate(dic)*self.rhs.evaluate(dic)       
    
        elif isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
    def derivative(self,variable='Matrix'):
        return self.lhs.derivative(variable)*self.rhs+self.lhs*self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        if type(self.lhs) == Constant:
            return self.lhs*self.rhs.primitive(variable)
            
        elif type(self.rhs) == Constant:
            return self.rhs*self.lhs.primitive(variable)
        
        else:
            print('Sorry, i can\'t do this!')
            

        
        
class DivNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(DivNode,self).__init__(lhs,rhs,'/',3,True,False)

    def evaluate(self, dic={}): 
        if not (isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str)): 
            return self.lhs.evaluate(dic)/self.rhs.evaluate(dic)       
    
        elif isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str):
            return "(%s) %s (%s)" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
        
    def derivative(self,variable='Matrix'):
        return (self.lhs.derivative(variable)*self.rhs-self.lhs*self.rhs.derivative(variable))/(self.rhs*self.rhs) 
        
class ExpNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(ExpNode,self).__init__(lhs,rhs,'**',4,False,True)
        #hiervan werkt de derivative nog niet, we hebben immers Ln nodig
    def evaluate(self, dic={}): 
        if not (isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str)): 
            return self.lhs.evaluate(dic)**self.rhs.evaluate(dic)       
    
        elif isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str):
            return "(%s) %s %s" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
    def primitive(self,variable):
        if type(self.rhs) == Constant:
            return (Constant(1)/(self.rhs+Constant(1)))*Variable(variable)*self
        #2^x nog toevoegen en daarna algemene errormessage
            
#numerieke integratie
def NumInt(function,variable,leftinterval,rightinterval,step): 
    a = leftinterval+0.5*step
    c = [function.evaluate({variable:a})]
    i = step
    while i+a<=rightinterval:
        c.append(function.evaluate({variable:i+a}))
        i=i+step
    return sum(c)*(a-leftinterval)*2
    
def TestFundThmOfCalculus(function,variable): 
    F = function.primitive(variable)
    L = F.evaluate({variable:1})
    R = F.evaluate({variable:4})
    D = R - L
    S = NumInt(function,'x',1,4,0.0001)
    if abs(D-S)<0.01:
        return 'The fundamental theorem of calculus is propably true (checked numerically).'
    else:
        return 'It seems that the fundamental theorem of calculus is false (that seems strange since it has already been proven)'
        
def PartialEvaluation(Expr, dic):
    return Expression.fromString(Expr.evaluate(dic))

#testomgeving 
a=Constant(4)
b=Constant(5)
c=Constant(7)
e=Variable('x')
print(Expression.fromString('(4+(5*7))'))
<<<<<<< HEAD

=======
print(expr.evaluate())
>>>>>>> 0d9b40a3ee53e5898f3b28f962a1a9d0eb16b91f
# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.

expres = Expression.fromString('5/(e+1)') 
print(expres.derivative('e'))
<<<<<<< HEAD
=======

>>>>>>> 0d9b40a3ee53e5898f3b28f962a1a9d0eb16b91f



expre=Expression.fromString('2+y+x+z*z') #volgens mij werkt het naar behoren
print(PartialEvaluation(expre,{'y':14,'x':2}))
print(expre)
print(expre.evaluate({'y':2})) 
a=expre.derivative('y')
print(a)
# print(NumInt(expre,'z',1,2,0.01))#yess! het werkt!
# polynoom = Expression.fromString('2+3*x+5*x**2+x**3')
# P=polynoom.primitive('x') # yess! dit werkt ook
# print(P.evaluate({'x':1}))
# print(P.evaluate())
#print(TestFundThmOfCalculus(polynoom,'x'))


#TODO: functies voor printen boomstructuur, printen zonder versimpeling.

print(Expression.fromString('1+0'))
print(Expression.fromString('(1+0)'))
print(Expression.fromString('(0+1)*2')) 
print(Expression.fromString('1*2'))
print(Expression.fromString('(1*1)+0'))



# print(expre.evaluate({'y':2}))
# f=e+e
# a=expre.derivative('y')
# print(a.evaluate({'z':0}))
# print(type(a))
# print(a)
# print(expr.evaluate())
# x=Constant(0)
# y=Constant(3)
# print((x+y)*g)
# print(NumInt(expre,'z',1,2,0.01))
# print(g.primitive('g'))
# polynoom = Expression.fromString('2+3*x+5*x**2+x**3')
# P=polynoom.primitive('x')
# print(P.evaluate({'x':1}))
# print(P.evaluate())


print(0 == str(0))

#willen we van 0-5 ook -5 maken? En hoe zit dat eigenlijk uberhaupt met min getallen, daar kunnen we niet echt mee rekenen volgens mij? ff testen.

# a = Expression.fromString('-3+5')

print(Expression.fromString('3/(5*5)'))
print(type(Expression.fromString('3/(5*5)')))

#uhm ik snap even niet waarom hij niks invult enzo, dus misschien moeten we hier morgen samen maar naar kijken ;)
#0+0 gaat nog niet goed ergens....??
a = Expression.fromString('x+1')
print(a.primitive('x'))
# b = a + a*a
# print(b.derivative())
# print(b)
<<<<<<< HEAD
# print(b.primitive('x'))
=======
# print(b.primitive('x'))
>>>>>>> 0d9b40a3ee53e5898f3b28f962a1a9d0eb16b91f

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
        
# check if a string represents a variable
# dit werkt nog niet, want hij geeft bij alles dat hij er wel een variabele van kan maken ;)
# ListOfVariables=[]
def isvar(string):
    try:
        Variable(string)
        Value = True and not isnumber(string) and not string in ['+', '-', '*', '/', '**','(',')']
        # if Value == True:
        #     ListOfVariables.append(str(Variable(string)))
        return Value
    except ValueError:
        return False
# zo met dit gekke lange statement geeft hij alleen bij letters wat we willen, misschien is het goed zo? Maar niet zo'n elegante oplossing. 
# misschien kunnen we al die voorwaardes weglaten als we de if statements in het shunting alg goed plaatsen.
  


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
        assoclist=['L','L','L','L','R']
        
        
        for token in tokens:
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
            elif isvar(token): # dit stukje toegevoegd
                # variables go directly to output as well
                output.append(Variable(token))
            elif token in oplist:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    if len(stack) == 0 or stack[-1] not in oplist:
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
            else:
                z=Variable(token)
                output.append(z)# unknown token
                print(z)
                
#                raise ValueError('Unknown token: %s' % token)

    
            
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
    
    def derivative(self, variable = 'Matrix'): #afgeleide van constante is 0
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
        
        #return "%s %s %s" % (lstring, self.op_symbol, rstring)# moet als laatste. Versimpeling werkt nog niet zoals ik wil :(
        

        # if self.op_symbol == '+':
        #     if self.lhs == Constant(0):
        #          return str(self.rhs)
        #     elif self.rhs == Constant(0):
        #          return str(self.lhs)
        #     else:
        #         return "%s %s %s" % (lstring, self.op_symbol, rstring)
        # elif self.op_symbol == '*':
        #     if self.lhs == Constant(0) or self.rhs == Constant(0):
        #         return str(Constant(0))
        #     if self.lhs == Constant(1):
        #         return str(self.rhs)
        #     elif self.rhs == Constant(1):
        #         return str(self.lhs)
        if (self.lhs.prec<self.prec) or (self.lhs.prec==self.prec and not self.lhs.assoc_left):#Doe haakjes om linkerkant immers bij de boom ((5*2)**5) moeten er haakjes om 5*2 in de string
            #als bv ((3**4)**5) dan prec=prec_links maar links is niet linksasso dus doe haakjes om (3**4)
            lstring = '('+lstring+')' #dit zorgt voor haakjes om lstring
        if (self.rhs.prec<self.prec) or (self.rhs.prec==self.prec and not self.rhs.assoc_right):#Doe haakjes om rechterkant immers bij de boom (3*(2+3)) moeten er haakjes om 2+3 in de string
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
            return "%s %s %s" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
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
            return "%s %s %s" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
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
            return "%s %s %s" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
    def derivative(self,variable='Matrix'):
        return self.lhs.derivative(variable)*self.rhs+self.lhs*self.rhs.derivative(variable) 
        
    def primitive(self,variable):
        if type(self.lhs) == Constant:
            return self.lhs*self.rhs.primitive(variable)
            
        if type(self.rhs) == Constant:
            return self.rhs*self.lhs.primitive(variable)

class DivNode(BinaryNode):
    def __init__(self,lhs,rhs):
        super(DivNode,self).__init__(lhs,rhs,'/',3,True,False)

    def evaluate(self, dic={}): 
        if not (isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str)): 
            return self.lhs.evaluate(dic)/self.rhs.evaluate(dic)       
    
        elif isinstance(self.lhs.evaluate(dic),str) or isinstance(self.rhs.evaluate(dic),str):
            return "%s %s %s" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
        
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
            return "%s %s %s" % (self.lhs.evaluate(dic), self.op_symbol, self.rhs.evaluate(dic))
        
    def primitive(self,variable):
        if type(self.rhs) == Constant:
            return (Constant(1)/(self.rhs+Constant(1)))*Variable(variable)*self
            
def NumInt(function,variable,leftinterval,rightinterval,step): #dit is de gebruikelijke Riemann Integratie, het lijkt goed te werken.
    a = leftinterval+0.5*step
    c = [function.evaluate({variable:a})]
    i = step
    while i+a<=rightinterval:
        c.append(function.evaluate({variable:i+a}))
        i=i+step
    return sum(c)*(a-leftinterval)*2
    
def TestFundThmOfCalculus(function,variable): #Als je dit een slecht idee vindt om deze functie toe te voegen kan ik dat ik begrijpen :)
    F = function.primitive(variable)
    L = F.evaluate({variable:1})
    R = F.evaluate({variable:4})
    D = R - L
    S = NumInt(function,'x',1,4,0.0001)
    if abs(D-S)<0.01:
        return 'The fundamental theorem of calculus is propably true (checked numerically).'
    else:
        return 'It seems that the fundamental theorem of calculus is false (that seems strange since it has already been proven)'

#testomgeving 
a=Constant(4)
b=Constant(5)
c=Constant(7)
e=Variable('x')
print(e)
print(a+b*(c+a))
print((a+b)*(c+a))
print(type(a+b*(c+a)))
expr = Expression.fromString('(4+(5*7))') # omdat we nu de print overschreven hebben kunnen we nooit meer de boomstr. printen, is dat niet onhandig?
print(expr)
# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.
hallo='Dit is raar'
print('Hallo Allemaal (%s)' % hallo)




#print(eval('3 + d'))
# ik snap het stukje van eval niet echt volgens mij, waarom staat dat in het shunting alg? en misschien zit daar ook het probleem van de error?
g = Variable('g')
der=g.derivative()
print(der)

print(Expression.fromString('4+5*7') == Expression.fromString('5*7+4'))
# g=(a*d)+b
# h=str(g)
# print(h)
# d=2
# eval(h)
# print(eval(h))
# k=a+b*d

# print(Expression.evaluate(k,{d:4}))
expre=Expression.fromString('2+z*z') #volgens mij werkt het naar behoren

print(type(expre))

print(expre.evaluate({'y':2}))
f=e+e
a=expre.derivative('y')#Jeej het werkt
print(type(a))
print(a)
print(expr.evaluate())
x=Constant(0)
y=Constant(3)
print((x+y)*g)
print(NumInt(expre,'z',1,2,0.01))#yess! het werkt!
print(g.primitive('g'))
polynoom = Expression.fromString('2+3*x+5*x**2+x**3')
P=polynoom.primitive('x') # yess! dit werkt ook
print(P.evaluate({'x':1}))
print(P.evaluate())

print(TestFundThmOfCalculus(polynoom,'x'))
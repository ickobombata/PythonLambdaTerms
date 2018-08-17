# named lambda term construction
# convention \x->xz\y->xyz

# constant ["a0"]
# application [App, Expr, Expr]
# lambda      [\, Name, Expr]

# substitution of named lambda terms
# ex: \x->xz\y->xyz [z -> \u->uv] === \x->x(\u->uv)\y->xy\u->uv

# conversion from nameless to named lambda terms

class C:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def sub(self, name, expr):
        if name.value == self.value:
            return expr
        return self

    def b_mol(self, Gamma, Psi):
        return self.b_mol_d(0, Gamma, Psi)

    def b_mol_d(self, d, Gamma, Psi):
        if self.value in Gamma:
           return NC(Gamma[self.value] + d)
        else:
            return NC(d - (1 + Psi[self.value]))

class App:
    def __init__(self, expr1, expr2):
        self.expr1, self.expr2 = expr1, expr2

    def __str__(self):
        return "(" + str(self.expr1) + " " + str(self.expr2) + ")"
        
    def sub(self, name, expr):
        return App(self.expr1.sub(name, expr), self.expr2.sub(name, expr))

    def b_mol(self, Gamma, Psi):
        return self.b_mol_d(0, Gamma, Psi)

    def b_mol_d(self, d, Gamma, Psi):
        return NApp(self.expr1.b_mol_d(d, Gamma, Psi),
            self.expr2.b_mol_d(d, Gamma, Psi))

class Abs:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def __str__(self):
        return "\\" + str(self.name) + "->" + str(self.expr)

    def sub(self, name, expr):
        if name == self.name:
            raise Exception("Can not sub bounded variable")
        return Abs(self.name, self.expr.sub(name, expr))

    def b_mol(self, Gamma, Psi):
        return self.b_mol_d(0, Gamma, Psi)

    def b_mol_d(self, d, Gamma, Psi):
        return NAbs(self.expr.b_mol_d(d + 1, Gamma, Psi))

# nameless lambda term construction
# convention \01\102

# constant ["12"]
# application [App, Expr, Expr]
# lambda      [\, Expr]

# substitution of nameless lambda terms
# ex: \01\102 [1 -> \01] === \0

# conversion from named to nameless lambda terms

class NC(C):
    def __init__(self, value):
        super().__init__(value)

    def inc(self, k, d):
        return NC(self.value if self.value < d else self.value + k)

    def d_s(self, Gamma, Psi):
        return self.d_s_d(0, Gamma, Psi)

    def d_s_d(self, d, Gamma, Psi):
        if self.value < d:
            return C(Psi[d - (1 + self.value)])
        else:
            return C(Gamma[self.value - d])

class NApp(App):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def inc(self, k, d):
        return NApp(self.expr1.inc(k, d), self.expr2.inc(k, d))

    def d_s(self, Gamma, Psi):
        return self.d_s_d(0, Gamma, Psi)

    def d_s_d(self, d, Gamma, Psi):
        return App(self.expr1.d_s_d(d, Gamma, Psi), self.expr2.d_s_d(d, Gamma, Psi))

class NAbs:
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return "\\ " + str(self.expr)

    def sub(self, name, expr):
        return NAbs(self.expr.sub(NC(name.value + 1), expr.inc(1, 0)))
    
    def inc(self, k, d):
        return NAbs(self.expr.inc(k, d + 1))

    def d_s(self, Gamma, Psi):
        return self.d_s_d(0, Gamma, Psi)

    def d_s_d(self, d, Gamma, Psi):
        return Abs(Psi[d], self.expr.d_s_d(d + 1, Gamma, Psi))

#Testing 


#\x->xz\y->xyz
x = C("x")
y = C("y")
z = C("z")
expr = Abs(x, App(App(x, z), Abs(y, App(App(x, y), z))))
print(expr)
a = C("a")
print(expr.sub(z, a))

# name contexts. I need 2 ... 
Gamma = {
    "z": 0
    }

Psi = {
    "x": 0,
    "y": 1,
}
print("Converted: " + str(expr.b_mol(Gamma, Psi)))


#1\0 1\1 0 2

nexpr = NApp(NC(0), NAbs(NApp(NApp(NC(0), NC(1)), NAbs(NApp(NApp(NC(1), NC(0)), NC(2))))))
print(nexpr)

print(nexpr.inc(1, 0))

print(nexpr.sub(NC(0), NC(1)))

# name contexts. I need 2 ... 
Gamma = {
    0: "z"
    }

Psi = {
    0: "x",
    1: "y"
}
print("Converted: " + str(nexpr.d_s(Gamma, Psi)))

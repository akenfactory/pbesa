class Antecedent():
    
    def __init__(self, template, template_property, value):
        self.template = template
        self.template_property = template_property
        self.value = value

class TestAntecedent():
    
    def __init__(self, operation, *parametres):
        self.parameters = []
        self.operation = operation
        for param in parametres:
            self.parameters.append(param)

class Consequent():
    
    def __init__(self, template, template_property, value):
        self.template = template
        self.template_property = template_property
        self.value = value

class Parameter():
    
    def __init__(self, template, template_property):
        self.template = template
        self.template_property = template_property

class FunctionConsequent():
    
    def __init__(self, fun, *parametres):
        self.parameters = []
        self.fun = fun
        for param in parametres:
            self.parameters.append(param)

class Rule:

    def __init__(self, name, *components):
        self.__antecedents = []
        self.__consequents = []
        self.name = name
        for component in components:
            if isinstance(component, Antecedent) or isinstance(component, TestAntecedent):
                self.__antecedents.append(component)
            else:
                self.__consequents.append(component)

    def get_antecedents(self):
        return self.__antecedents

    def get_consequents(self):
        return self.__consequents

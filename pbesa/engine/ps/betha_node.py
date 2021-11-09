from .psagent.rule import FunctionConsequent, Parameter, TestAntecedent

class BethaNode():

    def __init__(self):
        self.name = None
        self.fire = False
        self.__consequents = []
        self.__alpha_node_dict = {}
        self.__antecedent_list = []

    def add_alpha_node(self, alpha_node):
        self.__alpha_node_dict[alpha_node.pattern] = alpha_node

    def add_consequent(self, consequent):
        self.__consequents.append(consequent)

    def add_antecedent(self, antecedent):
        self.__antecedent_list.append(antecedent)

    def add_element_list(self, lst, element):
        no_exist = True
        for ele in lst:
            if ele.id == element.id:
                no_exist = False
        if no_exist:
            lst.append(element)

    def evaluate(self):
        #print("")
        #print("---------------------------------[%s]:" % self.name)
        var_dict = {}
        test_list = []
        tuple_mlist = []
        template_dict = {}
        #-------------------------------------------------
        # Agrupa los templates
        for antecedent in self.__antecedent_list:
            if isinstance(antecedent, TestAntecedent):
                test_list.append(antecedent)
            else:
                if not antecedent.template in template_dict:
                    template_dict[antecedent.template] = []
                template_dict[antecedent.template].append(antecedent)
        #-------------------------------------------------
        # Compardores de valor
        # Itera los templates
        memory_mlist = []
        for template, antecedent_list in template_dict.items():
            #print("template", template)
            alpha_node = self.__alpha_node_dict[template]
            memory = alpha_node.alpha_memory
            # Filtra la memoria iterando y evaluando los 
            # antecedentes
            for antecedent in antecedent_list:
                fact_list = []
                for fact in memory:
                    if not antecedent.value and antecedent.template_property in fact.obj:
                        # Caso que el valor del 
                        # antecedente es nulo
                        self.add_element_list(fact_list, fact)
                    elif isinstance(antecedent.value, str) and "?" in antecedent.value:
                        # Caso en el que el valor 
                        # es una varible
                        self.add_element_list(fact_list, fact)
                        # Agrupa las variables
                        if not antecedent.value in var_dict:
                            var_dict[antecedent.value] = []
                        var_dict[antecedent.value].append(antecedent) 
                    else:
                        # Caso que el antecedente refiere 
                        # a un objeto
                        property_value = fact.obj[antecedent.template_property]
                        if antecedent.template_property in fact.obj: 
                            if property_value == antecedent.value:
                                # Caso en que el valor 
                                # coincide
                                self.add_element_list(fact_list, fact)
                memory = fact_list
            memory_mlist.append(memory)
        #-----------------------------------------
        # Genera la combinacion
        for fact_list in memory_mlist:
            list_b = []
            result_list = []
            for fact_a in fact_list:
                result_list.append([fact_a])
            list_a = result_list
            if len(tuple_mlist) > 0:
                list_b = tuple_mlist
                result_list = []
                for fact_a in list_a:
                    for fact_b in list_b:
                        com_tmp = []
                        com_tmp.extend(fact_a)
                        com_tmp.extend(fact_b)
                        result_list.append(com_tmp)
                tuple_mlist = result_list
            else:
                tuple_mlist = list_a
        #print("===== Comparadores de Valor ======")
        #print(len(tuple_mlist))
        """
        for fct_list in tuple_mlist:
            for fact in fct_list:
                print("[fact>", fact.template, "]:", fact.__dict__['id'][-10:])
            print("----------------------------------")
        """
        #print("==================================")
        # Valida Cardinalidad
        if len(tuple_mlist) > 0:
            #print("template_dict", len(template_dict))
            #print("tuple_mlist[0]", len(tuple_mlist[0]))
            if not len(template_dict) == len(tuple_mlist[0]):
                tuple_mlist = []

        #-------------------------------------------------
        # Valida los comparadores de operacion
        if len(test_list) and len(tuple_mlist) > 0:
            index = 0
            rm_mlist = []
            # Itera tupla por tupla
            for fct_list in tuple_mlist:
                match = True
                # Itera los comparadores de operacion
                # binarios
                for antecedent in test_list:
                    #-------------------------------------
                    # Obtiene el primer parametro
                    fact_param1 = {}
                    param1 = antecedent.parameters[0]
                    if isinstance(param1, Parameter):
                        # Caso variable  
                        for i in range(0, len(fct_list)):
                            fact = fct_list[i]
                            if fact.template == param1.template:
                                fact_param1['index'] = i
                                fact_param1['obj'] = fact
                                fact_param1['value'] = fact.obj[param1.template_property]
                    else:
                        # Caso valor
                        fact_param1['index'] = None
                        fact_param1['obj'] = None
                        fact_param1['value'] = param1
                    #-------------------------------------
                    # Obtiene el segundo parametro
                    fact_param2 = {}
                    param2 = antecedent.parameters[1]
                    if isinstance(param2, Parameter):
                        # Caso variable    
                        for i in range(0, len(fct_list)):
                            fact = fct_list[i]
                            if fact.template == param2.template:
                                fact_param2['index'] = i
                                fact_param2['obj'] = fact
                                fact_param2['value'] = fact.obj[param2.template_property]
                    else:
                        # Caso valor
                        fact_param2['obj'] = None
                        fact_param2['obj'] = None
                        fact_param2['value'] = param2
                    #-------------------------------------
                    # Evalua la operacion
                    if fact_param1 and fact_param2:                            
                        if antecedent.operation == "=":
                            match &= fact_param1['value'] == fact_param2['value']
                        elif antecedent.operation == ">":
                            match &= fact_param1['value'] > fact_param2['value']
                        elif antecedent.operation == "<":
                            match &= fact_param1['value'] < fact_param2['value']
                        elif antecedent.operation == ">=":
                            match &= fact_param1['value'] >= fact_param2['value']
                        elif antecedent.operation == "<=":
                            match &= fact_param1['value'] <= fact_param2['value']
                    else:
                        # Caso que el template no coincide
                        match = False
                if not match:
                    # Caso donde no pasa la operacion se 
                    # mantiene el indice para escluir 
                    # la tupla
                    rm_mlist.append(index)
                index += 1
            #---------------------------------------------
            # Elimina las tuplas que no pasaron
            if len(rm_mlist) > 0:
                index = 0
                new_tuple_mlist = []
                for fct_list in tuple_mlist:
                    if not index in rm_mlist:
                        new_tuple_mlist.append(fct_list)
                    index += 1
                tuple_mlist = new_tuple_mlist 
            #print("=== Comparadores de Operacion ====")
            #print(len(tuple_mlist))
            """
            print("=> rm_mlist", len(rm_mlist))
            for fct_list in tuple_mlist:
                for fact in fct_list:
                    print("[fact>", fact.template, "]:", fact.__dict__['id'][-10:])
                print("----------------------------------")
            """
            #print("==================================")
            
        #-------------------------------------------------
        # Valida los comparadores de relacion
        if len(var_dict) and len(tuple_mlist) > 0:
            index = 0
            rm_mlist = []
            # Itera tupla por tupla
            for fct_list in tuple_mlist:
                #print("+++", index)
                # Itera los grupos de variable
                for key, antecedent_list in var_dict.items():
                    #print("---", key)
                    value = None
                    # Itera los antecedentes del grupo
                    for antecedent in antecedent_list:
                        # Valida los hechos de la tupla 
                        # reacionados
                        for fact in fct_list:
                            if fact.template == antecedent.template:
                                if not value:
                                    value = fact.obj[antecedent.template_property]
                                """
                                print(
                                    "t:", antecedent.template, 
                                    "p:", antecedent.template_property,
                                    "vp:", fact.obj[antecedent.template_property][-10:],
                                    "v;", value[-10:])
                                """
                                if not value == fact.obj[antecedent.template_property]:
                                    if not index in rm_mlist:
                                        rm_mlist.append(index)
                                        #print(rm_mlist)
                index += 1
            #---------------------------------------------
            # Elimina las tuplas que no pasaron
            if len(rm_mlist) > 0:
                index = 0
                new_tuple_mlist = []
                for fct_list in tuple_mlist:
                    if not index in rm_mlist:
                        new_tuple_mlist.append(fct_list)
                    index += 1
                tuple_mlist = new_tuple_mlist
            #print("==== Comparadores de Relacion ====")
            #print(len(tuple_mlist))
            """
            print("=> rm_mlist", len(rm_mlist))
            for fct_list in tuple_mlist:
                for fact in fct_list:
                    print("[fact>", fact.template, "]:", fact.__dict__['id'][-10:])
                print("----------------------------------")
            """
            #print("==================================")

        #-------------------------------------------------
        # Verifica y dispara
        self.fire = False
        if len(tuple_mlist) > 0:
            if len(tuple_mlist) > 1:
                # Caso de mas de una tupla
                for fct_list in tuple_mlist:
                    #print("")
                    #print("________________________")
                    for consequent in self.__consequents:
                        if isinstance(consequent, FunctionConsequent):
                            if len(consequent.parameters) > 0:
                                data = {}
                                for param in consequent.parameters:
                                    #print("param:", param.template, param.template_property)
                                    for fact in fct_list:
                                        if fact.template == param.template:
                                            data[param.template_property] = fact.obj[param.template_property]
                                if data:
                                    consequent.fun(data)
                                    self.fire = True
                            else:
                                consequent.fun()
                                self.fire = True
            elif len(tuple_mlist) > 0:
                # Caso de una sola tupla
                #print("Caso de una solo tupla")
                #print("")
                #print("________________________")
                for consequent in self.__consequents:
                    if isinstance(consequent, FunctionConsequent):
                        if len(consequent.parameters) > 0:
                            data = {}
                            for param in consequent.parameters:
                                #print("param:", param.template, param.template_property)
                                for fact in tuple_mlist[0]:
                                    if fact.template == param.template:
                                        data[param.template_property] = fact.obj[param.template_property]
                            consequent.fun(data)
                            self.fire = True
                        else:
                            consequent.fun()
                            self.fire = True
        if self.fire:
            print("---------------------------------[%s]:" % self.name)
            print(len(tuple_mlist))
            for fct_list in tuple_mlist:
                for fact in fct_list:
                    print("[fact>", fact.template, "]:", fact.__dict__['id'][-10:])
                print("..............................")
            print("---------------------------------")
            print("")

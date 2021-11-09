class Directory(object):
    class __Directory:
        
        def __init__(self):
            self.containerList = []
            self.agentList = []
                    
        def addContainer(self, container):
            self.containerList.append(container)

        def addAgent(self, agent):
            self.agentList.append(agent)

        def getContainers(self):
        	return self.containerList

        def getAgents(self):
        	return self.agentList

        def resetAgentList(self):
        	self.agentList = []

        def removeAgent(self, agent): 
            for ag in self.agentList:
                if ag['agent'] == agent:
                    self.agentList.remove(ag)
                    
    instance = None
    def __new__(cls):
        if not Directory.instance:
            Directory.instance = Directory.__Directory()
        return Directory.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)

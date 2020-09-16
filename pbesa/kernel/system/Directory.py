from .exceptions import SystemException

class Directory(object):
    class __Directory:
        
        def __init__(self):
            self.containerList = []
            self.agentList = []
            self.gateway = None
            self.checkToList = None
                    
        def addContainer(self, container):
            self.containerList.append(container)

        def addAgent(self, agent):
            self.agentList.append(agent)

        def getContainers(self):
        	return self.containerList

        def getAgents(self):
        	return self.agentList
        
        def setAgentList(self, agentList):
            self.agentList = agentList
            
        def getAgent(self, agentID):
            for agent in self.agentList:
                if agentID == agent['agent']:
        	        return agent
            return None

        def resetAgentList(self):
        	self.agentList = []

        def removeAgent(self, agent): 
            for ag in self.agentList:
                if ag['agent'] == agent:
                    self.agentList.remove(ag)

        def setCheckList(self, gateway, checkToList):
            self.gateway = gateway
            self.checkToList = checkToList
        
        def checkFull(self, containerName):
            if self.checkToList:
                if containerName in self.checkToList:
                    self.checkToList.remove(containerName)
                    if len(self.checkToList) == 0:
                        self.gateway.put(None)
                else:
                    raise SystemException('Container name: "%s" does not match' % containerName)
                    
    instance = None
    def __new__(cls):
        if not Directory.instance:
            Directory.instance = Directory.__Directory()
        return Directory.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)

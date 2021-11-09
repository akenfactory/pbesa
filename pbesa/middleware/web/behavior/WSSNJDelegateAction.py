from ...kernel.agent.Action import Action

class WSSNJDelegateAction(Action):
    
    def execute(self, data):
        request = data['request']
        try:             
            dto = {'context': request['context'], 'data': request['data']}

            if request['context'] == 'register' or request['context'] == 'login':
                agID = self.agent.getFreePool()            
                if agID:
                    socket = data['socket']
                    self.adm.setEndPoint(agID, socket)
                    data = request['data']
                    self.agent.suscribeAgent(data['id'], agID)
                    rst = self.adm.sendEvent(agID, request['event'], dto)
                    if not rst:
                        self.responseError(data)
                else:
                    print('WARN::: All agent is busy.')
                    self.responseError(data)
            else:
                agID = None
                if request['context'] == 'logout':
                    data = request['data']
                    agID = self.agent.getAgentID(data['id'])
                    self.agent.toPool(data['id'], agID)
                else:
                    agID = self.agent.getAgentID(request['agent'])                    
                
                rst = self.adm.sendEvent(agID, request['event'], dto)
                if not rst:
                    agID = self.agent.getFreePool()
                    socket = data['socket']
                    self.adm.setEndPoint(agID, socket)
                    self.agent.suscribeAgent(request['agent'], agID)
                    rst = self.adm.sendEvent(agID, request['event'], dto)
                    if not rst:
                        self.responseError(data)

        except Exception as inst:
            print('Controled ecxeption in WSSNJDelegateAction: ')
            print('MSG: ', inst)
            self.responseError(data)
            

    def responseError(self, data):
        dto = {
            'state':'ERROR',
            'context':'None',
            'command': 'None',
            'msg': 'None',
            'options': []
        }
        socket = data['socket']
        dto = str(dto)
        dto = dto.replace("'", "\"") + '\n'
        socket.sendall(dto.encode())            
        
from TokenForce.KernelTK.Util.Log import Log
from TokenForce.KernelTK.SystemTK.Adm import Adm
from TokenForce.KernelTK.AgentTK.ActionTK import ActionTK

class WSRequestAction(ActionTK):
    
    def execute(self, data):
        request = data['request']
        self.agent.requestID = self.agent.requestID + 1
        rqstID = str(self.agent.requestID)
        self.agent.requestTable[rqstID] = data['socket']
        try:             
            Log().info('[WS-REQUEST]: Request-ID: ' + rqstID + '. To agent: ' + request['agent'] + ', event: ' + request['event'] + '.')                    
            dto = {'requestID': rqstID, 'context': request['context'], 'data': request['data']}
            Adm().sendEvent(request['agent'], request['event'], dto)	    
        except Exception as inst:
            print('Controled ecxeption: ')
            print('MSG: ', inst)
            dto = {
                'state':'ERROR',
                'context':'None',
                'command': 'None',
                'msg': 'None',
                'options': []
            }
            response = {'requestID': rqstID, 'data': dto}
            self.adm.sendEvent('front_controller', 'ws_response', response)
    


import uuid

class Fact():
    
    def __init__(self, template, obj):
        self.id = None
        self.template = template
        self.obj = obj
    
    def to_dict(self):
        dto = {}
        dto["id"] = self.id
        dto["template"] = self.template
        dto["obj"] = self.obj
        return dto

    def update_id(self, prop):
        if not self.id:
            if prop in self.obj:
                self.id = "%s_%s" % (self.template, self.obj[prop])
            else: 
                self.id = self.template

    def generate_id(self):
        self.id = str(uuid.uuid1())

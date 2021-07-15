
class BaseClass:
    def __init__(self, attributes, defaults):
        self.load(attributes, defaults)
    
    def export(self):
        attributes = vars(self)
        attributes.pop("defaults")
        return attributes
    
    def load(self, attributes, defaults):
        for name, value in defaults.items():
            if name not in attributes:
                setattr(self, name, value)
            else:
                setattr(self, name, attributes[name])

from ml.ml import ml

class NullML(ml):
  
    def predict(self):
        return None
        
    def train(self):
        pass

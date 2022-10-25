import json

class Util():
    
    def __init__():
        super()
    
    def generarJSON( filename):

        data = {
            "loss": [],
            "predictions": []
        }

        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    
    def guardarLoss( filename ,loss):

        with open(filename, 'r') as file:
            data = json.load(file)

        data['loss'].append(loss)

        with open(filename, 'w') as file:
            json.dump(data, file)

    def guardarPrediction( filename, datas):

        with open(filename, 'r') as file:
            data = json.load(file)

        data['predictions'].append(datas)

        with open(filename, 'w') as file:
            json.dump(data, file)

        




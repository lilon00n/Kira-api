clientsList = []


class Client:
    def __init__(self, code, logo, ext):
        self.code = code
        self.logo = logo
        self.ext = ext


def populateClients():

    qa = Client("HFK139", "serviestampados.png", "png")
    daet = Client("DAETWY", "daetwylerMX.png", "png")
    flexo = Client("FLHN01", "FlexoDigital-01.png", "png")

    clientsList.append(qa)
    clientsList.append(daet)
    clientsList.append(flexo)


def findClient(clientCode):
    for client in clientsList:
        if client.code == clientCode:
            return client


populateClients()

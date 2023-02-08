from api import Server


def serve():
    print("Starting server")
    Server().serve()


if __name__ == '__main__':
    print("Starting the app")
    serve()

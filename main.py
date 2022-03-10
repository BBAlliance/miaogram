from utils import app

def main():
    client = app.initClient()
    import controllers
    client.run()

if __name__ == "__main__":
    main()

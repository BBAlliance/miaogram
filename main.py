from utils import app, config

def main():
    config.prepare()
    config.reloadConfig()
    config.migrate()
    
    client = app.initClient()
    import controllers
    client.run()

if __name__ == "__main__":
    main()

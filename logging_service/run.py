from time import sleep

from app import create_app

app = create_app()
@app.route('/')
def hello():
    return 'Hello, World! this application runing on 192.168.0.105'

if __name__ == "__main__":
    print("Starting the application... (sleep 20 seconds)")
    sleep(20) # wait for kafka to be ready
    app.run(host="0.0.0.0", port=5000, debug=True)
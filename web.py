from webinterface import app, handlers, fs, av, seqc


def main():
    app.app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
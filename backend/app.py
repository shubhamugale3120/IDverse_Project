from backend import create_app

app = create_app()

if __name__ == "__main__":
    # print routes at startup (handy while debugging)
    print(app.url_map)
    app.run(debug=True)

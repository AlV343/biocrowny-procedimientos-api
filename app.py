@app.route("/", methods=["GET", "HEAD"])
def root():
    return "Biocrowny API OK", 200

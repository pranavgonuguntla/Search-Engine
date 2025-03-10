from flask import Flask, render_template, request
import queryProcessor as qp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    results = []

    if request.method == "POST":
        query = request.form["query"].strip()
        if query:
            id_list = qp.query_document_match(query) 
            urls = qp.retrieve_urls(id_list)  
            results = [{"url": url, "rank": i+1} for i, url in enumerate(urls[:5])]

    return render_template("index.html", query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)  
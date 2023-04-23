from Savings import app
from flask_ngrok import run_with_ngrok

# run_with_ngrok(app)
if __name__ == "__main__":
	app.run(debug=True,port=8080)
	# app.run()


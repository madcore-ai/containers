from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

app = Flask(__name__)

english_bot = ChatBot("English Bot",silence_performance_warning=True)
english_bot.set_trainer(ChatterBotCorpusTrainer)
english_bot.train("chatterbot.corpus.english")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process_chat")
def get_raw_response():
	try:
		chat_val = str(request.args.get('chat_txt'))
		return str(english_bot.get_response(chat_val))
	except Exception,e:
		print "error..",e


if __name__ == "__main__":
   	app.run(debug=True, host='0.0.0.0', port=9019)

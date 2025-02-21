import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend requests
CORS(app, resources={r"/generate-thread": {"origins": "https://twitter-thread-generator-t34b.vercel.app"}})


# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def blog_to_tweets(blog_text):
    """
    Converts a blog into an engaging Twitter thread using AI.
    """
    prompt = (
        """You are a social media strategist specializing in viral Twitter threads.
            Your task is to convert the following blog into an engaging Twitter thread.
            
            Guidelines:
            ✅ Strong Hook: Start with an attention-grabbing tweet.
            ✅ Concise & Engaging: Each tweet must be under 280 characters.
            ✅ Logical Flow: Tweets should connect smoothly.
            ✅ Balanced Content: Mix facts, insights, and rhetorical questions.
            ✅ No Repetitive Formatting: Avoid "Tweet 1: X/Y".
            ✅ Strong CTA: End with a discussion prompt.

            Example:
            🚀 AI is evolving FAST… but can it ever match human intelligence? Let’s break it down! 👇 #AI #AGI
            
            Now, generate a structured Twitter thread based on this blog:
            """
        f"\n\n{blog_text}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert at crafting viral Twitter threads."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
    )

    response = chat_completion.choices[0].message.content
    tweets = response.split("\n")

    return [tweet.strip() for tweet in tweets if tweet.strip()]

@app.route("/", methods=["GET"])
def generate_thread():
    """
    API endpoint to generate a Twitter thread from a blog.
    """
    data = request.get_json()
    blog_text = data.get("blog_text", "")

    if not blog_text:
        return jsonify({"error": "Blog text is required."}), 400

    try:
        tweets = blog_to_tweets(blog_text)
        return jsonify({"thread": tweets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get the assigned PORT from Render
    app.run(debug=True, host="0.0.0.0", port=port)

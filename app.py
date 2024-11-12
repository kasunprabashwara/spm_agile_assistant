from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from model import get_response
import os
import re

app = FastAPI()

# Serve static files (like CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

class Query(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    # Serve the HTML for the chatbot GUI
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot Interface</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="chat-container">
            <div id="chat-box" class="chat-box"></div>
            <form id="chat-form" class="chat-form">
                <input type="text" id="question" name="question" placeholder="Ask a question..." autocomplete="off" required />
                <button type="submit">Send</button>
            </form>
        </div>
        <script>
            const chatForm = document.getElementById("chat-form");
            const chatBox = document.getElementById("chat-box");

            chatForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                const question = document.getElementById("question").value;
                
                // Display user question in chat box
                const userMessage = document.createElement("div");
                userMessage.className = "chat-message user";
                userMessage.textContent = question;
                chatBox.appendChild(userMessage);
                chatBox.scrollTop = chatBox.scrollHeight;

                // Send question to backend
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question }),
                });
                
                const result = await response.json();
                
                const botMessage = document.createElement("div");
                botMessage.className = "chat-message bot";

                // Use innerHTML to render HTML-formatted response
                botMessage.innerHTML = result.answer;
                chatBox.appendChild(botMessage);
                chatBox.scrollTop = chatBox.scrollHeight;

                // Clear input
                document.getElementById("question").value = "";
            });
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_class=JSONResponse)
async def chat(query: Query):
    try:
        response = get_response(query.question)
        
        # Format the response to include HTML formatting
        formatted_response = format_response(response)

        return {"answer": formatted_response}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

def format_response(response: str) -> str:
    """
    Function to format the response into HTML-friendly format
    - Converts newlines to <br> tags
    - Converts **bold** to <strong>bold</strong>
    - Converts numbered lists (1. item) into <ol> and <li> tags
    """
    # Replace newlines with <br> tags
    response = response.replace("\n", "<br>")

    # Replace markdown-style bold with HTML <strong> tags
    response = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", response)

    # Convert numbered lists into <ol> and <li> tags
    response = re.sub(r"(\d+)\.\s(.*?)(?=\s*\d+\.|\s*$)", r"<li>\2</li>", response)
    response = re.sub(r"<li>(.*?)</li>", r"<ol><li>\1</li></ol>", response, count=1)

    return response

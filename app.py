from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from model import get_response
import os

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
                botMessage.textContent = result.answer;
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
        return {"answer": response}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

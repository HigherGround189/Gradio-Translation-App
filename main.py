import gradio as gr
import requests

# 1. JS to handle SpeechRecognition and update the transcript box
speech_js = """
function initSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.interimResults = true;
    recognition.lang = 'en-GB';

    const transcriptDiv = document.getElementById('transcript');
    const inputElement = transcriptDiv.querySelector('textarea');
    console.log(inputElement)

    recognition.onresult = e => {
        // Find the actual input element inside the transcript div
        
        if (inputElement) {
            inputElement.value = Array.from(e.results).map(r => r[0].transcript).join(' ');
            // Trigger input event to update Gradio's state
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
    
    window.startRec = () => recognition.start();
    window.stopRec = () => recognition.stop();

    console.log("Speech recognition initialized");
}
"""

# 2. Python function to call your local LLM summarizer
def summarize(text):
    # adjust URL/port as needed
    resp = requests.post("http://localhost:8000/summarize", json={"text": text})
    return resp.json().get("summary", "Error generating summary.")

with gr.Blocks(js=speech_js) as demo:
    transcript = gr.Textbox(label="Live Transcript", elem_id="transcript")
    summary = gr.Textbox(label="Summary")
    btn_start = gr.Button("🎤 Start Recording")
    btn_summ = gr.Button("🔀 Translate")

    # 3. Wire buttons: start/stop via JS; summarization via Python
    btn_start.click(fn=None, inputs=None, outputs=None, js="() => window.startRec()")
    btn_summ.click(fn=lambda _: None, inputs=None, outputs=None, js="() => window.stopRec()")
    btn_summ.click(fn=summarize, inputs=transcript, outputs=summary)

demo.launch()
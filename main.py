import gradio as gr  # type: ignore
import requests  # type: ignore

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

theme = gr.themes.Default(text_size="lg")

# 2. Python function to call your local LLM summarizer
def getTranslation(text):
    # adjust URL/port as needed
    resp = requests.post("http://localhost:5003/getTranslation", json={"text": text})
    return resp.json().get("translate", "Error generating translation.")

with gr.Blocks(js=speech_js, theme=theme) as demo:
    with gr.Row():
        # Left column for transcript
        with gr.Column():
            transcript = gr.Textbox(label=" 🎥  Live Transcript", elem_id="transcript", lines=15)
            btn_start = gr.Button("🎤 Start Recording")
        
        # Right column for translation
        with gr.Column():
            translate = gr.Textbox(label="💬 Translate", lines=15)
            btn_summ = gr.Button("🔀 Translate")
    
    # 3. Wire buttons: start/stop via JS; summarization via Python
    btn_start.click(fn=None, inputs=None, outputs=None, js="() => window.startRec()")
    btn_summ.click(fn=lambda _: None, inputs=None, outputs=None, js="() => window.stopRec()")
    btn_summ.click(fn=getTranslation, inputs=transcript, outputs=translate)

demo.launch()
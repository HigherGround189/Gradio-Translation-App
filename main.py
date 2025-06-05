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
            inputElement.value = Array.from(e.results)
                                    .map(r => r[0].transcript)
                                    .join(' ');
            // Trigger input event to update Gradio's state
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
    
    window.startRec = () => recognition.start();
    window.stopRec = () => recognition.stop();
    console.log("Speech recognition initialized");
}
"""

css = """
#lang-target-box, #lang-source-box {
    flex-wrap: wrap;
    display: flex;
    align-content: center;
}

#lang-target-box h3, .svelte-vuh1yp, .prose.svelte-lag733, .md.svelte-7ddecg.prose {
    width: 100%;
}
"""

theme = gr.themes.Default(text_size="lg")

# 2. Python function to call your local LLM summarizer (stub logic remains the same)
def getTranslation(text, isEnglish=True):
    if isEnglish:
        resp = requests.post("http://localhost:5003/translate", json={"text": text})
    else:
        resp = requests.post("http://localhost:5004/translate", json={"text": text})
    return resp.json().get("translation", "Error generating translation.")

with gr.Blocks(js=speech_js, css=css, theme=theme) as demo:
    # --- LANGUAGE INDICATORS ROW ---
    with gr.Row(equal_height=True):
        # Left indicator (current source language), right-aligned
        with gr.Column():
            lang_source = gr.Markdown(
                f"### <div style='text-align: right; display: block;'>Source: English</div>",
                elem_id="lang-source-box"
            )
        # Swap button in the middle
        with gr.Column(scale=0.2, min_width=50):
            swap_btn = gr.Button(
                "⇆",
                elem_id="swap-language-btn",
                value=None  # no logic hooked yet
            )
        # Right indicator (current target language)
        with gr.Column():
            lang_target = gr.Markdown(
                f"### <div style='text-align: left;display: block;'>Target: Chinese</div>",
                elem_id="lang-target-box"
            )

    # --- MAIN TRANSCRIPT / TRANSLATION ROW ---
    with gr.Row():
        # Left column: live transcript
        with gr.Column():
            transcript = gr.Textbox(
                label=" 🎥 Live Transcript",
                elem_id="transcript",
                lines=15
            )
            btn_start = gr.Button("🎤 Start Recording")
        # Right column: translated output
        with gr.Column():
            translate = gr.Textbox(
                label="💬 Translate",
                lines=15
            )
            btn_summ = gr.Button("🔀 Translate")

    # --- WIRE BUTTONS ---
    btn_start.click(fn=None, inputs=None, outputs=None, js="() => window.startRec()")
    btn_summ.click(
        fn=getTranslation,
        inputs=transcript,
        outputs=translate,
        js="() => window.stopRec()"
    )

demo.launch()
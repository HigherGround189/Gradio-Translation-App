import gradio as gr # type: ignore
import requests # type: ignore

# 1. JS to handle SpeechRecognition and update the transcript box
#    Revised with IIFE structure and language toggle
speech_js = """
function initSpeech() {
    // This is an IIFE (Immediately Invoked Function Expression)
    // It helps to avoid polluting the global scope and ensures code runs immediately.

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.error("Speech Recognition API not supported in this browser.");
        return; // Stop further execution of this script block
    }

    // Create and configure the speech recognition instance
    // Make it global so setSpeechLang and other functions can access it
    window.gradioSpeechRecognition = new SpeechRecognition();
    window.gradioSpeechRecognition.interimResults = true;
    
    // Global variable to track current language
    window.currentSpeechLang = 'en-GB';  // Default language
    window.gradioSpeechRecognition.lang = window.currentSpeechLang;

    // Event handler for when speech is recognized
    window.gradioSpeechRecognition.onresult = event => {
        const transcriptDiv = document.getElementById('transcript'); // elem_id of the Gradio Textbox
        const inputElement = transcriptDiv ? transcriptDiv.querySelector('textarea') : null;
        
        if (inputElement) {
            inputElement.value = Array.from(event.results)
                                    .map(r => r[0].transcript)
                                    .join(''); // Using empty join for continuous speech, or ' ' for space-separated
            
            // Trigger input event to update Gradio's state if necessary
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            // console.warn("Transcript input element not found for speech result.");
        }
    };

    // Event handler for errors
    window.gradioSpeechRecognition.onerror = event => {
        console.error('Speech recognition error:', event.error, 'Message:', event.message);
        let errorMsg = 'Speech recognition error: ' + event.error;
        if (event.message) errorMsg += " - " + event.message;
        // Consider displaying this to the user in a dedicated UI element.
    };
    
    // Event handler for when recognition starts
    window.gradioSpeechRecognition.onstart = () => {
        console.log("Speech recognition started. Language: " + window.gradioSpeechRecognition.lang);
    };

    // Event handler for when recognition ends
    window.gradioSpeechRecognition.onend = () => {
        console.log("Speech recognition ended.");
    };

    // --- Globally accessible functions for Gradio ---

    window.startRec = () => {
        if (window.gradioSpeechRecognition) {
            try {
                // It's often good practice to stop before starting,
                // especially if language or other settings might have changed.
                window.gradioSpeechRecognition.stop(); // Safe to call even if not running
                window.gradioSpeechRecognition.start();
            } catch (e) {
                console.warn("Could not start speech recognition (it might be busy or an API issue):", e);
            }
        } else {
            console.error("Speech recognition object not found (window.gradioSpeechRecognition).");
        }
    };

    window.stopRec = () => {
        if (window.gradioSpeechRecognition) {
            window.gradioSpeechRecognition.stop();
        } else {
            console.error("Speech recognition object not found (window.gradioSpeechRecognition).");
        }
    };

    window.setSpeechLang = (lang) => {
        if (window.gradioSpeechRecognition) {
            const recognizer = window.gradioSpeechRecognition;
            console.log("Attempting to set speech language to: " + lang);
            // Stop any ongoing recognition before changing the language.
            recognizer.stop(); 
            recognizer.lang = lang;
            window.currentSpeechLang = lang;
            console.log("Speech recognition language set to: " + lang);
            // User will need to click "Start Recording" again.
        } else {
            console.error("Speech recognition object not found (window.gradioSpeechRecognition) during setSpeechLang.");
        }
    };

    // NEW FUNCTION: Toggle between English and Chinese
    window.toggleSpeechLang = () => {
        const newLang = window.currentSpeechLang === 'en-GB' 
            ? 'cmn-Hans-CN' 
            : 'en-GB';
        
        window.setSpeechLang(newLang);
        return newLang;  // Return new language for debugging
    };

    // Attach click handler to swap button
    document.addEventListener('click', (event) => {
        if (event.target.id === 'swap-language-btn') {
            window.toggleSpeechLang();
        }
    });

    console.log("Speech recognition script loaded and IIFE executed. Current language: " + window.currentSpeechLang);
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


.md.svelte-7ddecg.prose h3 {
    text-align: center;
}
"""
theme = gr.themes.Default(text_size="lg")

# --- Constants for languages ---
LANG_ENGLISH = "English"
LANG_CHINESE = "Chinese"
SPEECH_LANG_ENGLISH = "en-GB"
SPEECH_LANG_CHINESE = "cmn-Hans-CN"

INITIAL_IS_ENGLISH_SOURCE = True

# 2. Python function to call your local LLM (updated)
def getTranslation(text, is_source_english):
    source_lang_name = LANG_ENGLISH if is_source_english else LANG_CHINESE
    target_lang_name = LANG_CHINESE if is_source_english else LANG_ENGLISH
    
    print(f"Attempting to translate from {source_lang_name} to {target_lang_name}. Raw input: '{text}'")
    
    if not text or not text.strip():
        print("Input text is empty. Returning pre-defined message.")
        return "Input text is empty. Nothing to translate."

    endpoint = "http://localhost:5003/translate" if is_source_english else "http://localhost:5004/translate"
    
    try:
        print(f"Sending request to: {endpoint}")
        resp = requests.post(endpoint, json={"text": text})
        resp.raise_for_status()
        translation_result = resp.json().get("translation")
        if translation_result is None:
            print("Error: 'translation' key not found in response JSON.")
            return "Error: Malformed response from translation server."
        print(f"Successfully received translation: {translation_result}")
        return translation_result
    except requests.exceptions.ConnectionError:
        error_msg = f"Error: Could not connect to the translation server at {endpoint} for {source_lang_name}."
        print(error_msg)
        return error_msg
    except requests.exceptions.HTTPError as e:
        error_msg = f"Error: Translation server returned an error ({e.response.status_code}) for {source_lang_name}."
        print(error_msg)
        return error_msg
    except requests.exceptions.JSONDecodeError:
        error_msg = "Error: Could not decode JSON response from the translation server."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred during translation: {str(e)}"
        print(error_msg)
        return error_msg

with gr.Blocks(js=speech_js, css=css, theme=theme) as demo:
    is_english_source_state = gr.State(INITIAL_IS_ENGLISH_SOURCE)

    with gr.Row(equal_height=True):
        with gr.Column():
            lang_source_md = gr.Markdown(
                f"### Source: {LANG_ENGLISH if INITIAL_IS_ENGLISH_SOURCE else LANG_CHINESE}\n",
                elem_id="lang-source-box"
            )
        with gr.Column(scale=0.2, min_width=50):
            swap_btn = gr.Button("⇆", elem_id="swap-language-btn")
        with gr.Column():
            lang_target_md = gr.Markdown(
                f"### Target: {LANG_CHINESE if INITIAL_IS_ENGLISH_SOURCE else LANG_ENGLISH}\n",
                elem_id="lang-target-box"
            )

    def swap_languages_logic(current_is_english_source):
        new_is_english_source = not current_is_english_source
        
        if new_is_english_source:
            source_display_lang = LANG_ENGLISH
            target_display_lang = LANG_CHINESE
        else:
            source_display_lang = LANG_CHINESE
            target_display_lang = LANG_ENGLISH
            
        new_lang_source_text = f"### Source: {source_display_lang}\n"
        new_lang_target_text = f"### Target: {target_display_lang}\n"

        print(f"Swapping languages. New source: {source_display_lang}")

        return {
            lang_source_md: new_lang_source_text,
            lang_target_md: new_lang_target_text,
            is_english_source_state: new_is_english_source
        }

    swap_btn.click(
        fn=swap_languages_logic,
        inputs=[is_english_source_state],
        outputs=[
            lang_source_md,
            lang_target_md,
            is_english_source_state
        ]
    )

    with gr.Row():
        with gr.Column():
            transcript_tb = gr.Textbox(
                label="🎥 Live Transcript",
                elem_id="transcript",
                lines=15,
                placeholder="Click 'Start Recording' and speak. Your words will appear here."
            )
            btn_start_rec = gr.Button("🎤 Start Recording" ) #, elem_id="start-rec-btn" # if you need to access it from JS by ID
        with gr.Column():
            translation_tb = gr.Textbox(
                label="💬 Translation",
                lines=15,
                placeholder="Translation will appear here after you click 'Translate'.",
                interactive=False
            )
            btn_translate = gr.Button("🔀 Translate")

    btn_start_rec.click(
        fn=None, 
        inputs=None, 
        outputs=None, 
        js="() => { if(window.startRec) { window.startRec(); } else { console.error('startRec function not found on window.'); } }"
    )
    
    btn_translate.click(
        fn=None, 
        inputs=None, 
        outputs=None, 
        js="() => { console.log('Translate button: attempting to stop recording.'); if(window.stopRec) { window.stopRec(); } else { console.error('stopRec function not found on window.'); } }"
    )
    
    btn_translate.click(
        fn=getTranslation,
        inputs=[transcript_tb, is_english_source_state],
        outputs=translation_tb
    )

demo.launch()
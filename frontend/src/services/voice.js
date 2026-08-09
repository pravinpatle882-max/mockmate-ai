// Voice Recording & Speech Recognition Service
class VoiceService {
  constructor() {
    this.recognition = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.initSpeechRecognition();
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';
    }
  }

  hasSpeechSupport() {
    return !!this.recognition || !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  startRecording(onTranscriptChange, onError) {
    this.audioChunks = [];
    this.isRecording = true;

    // 1. Web Speech API live recognition
    if (this.recognition) {
      this.recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (onTranscriptChange && finalTranscript) {
          onTranscriptChange(finalTranscript);
        }
      };

      this.recognition.onerror = (err) => {
        console.warn("Web Speech API error:", err);
      };

      try {
        this.recognition.start();
      } catch (e) {
        console.warn("Recognition start error:", e);
      }
    }

    // 2. MediaRecorder for audio blob creation
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          this.mediaRecorder = new MediaRecorder(stream);
          this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
              this.audioChunks.push(event.data);
            }
          };
          this.mediaRecorder.start();
        })
        .catch(err => {
          console.warn("Microphone access denied:", err);
          if (onError) onError("Microphone permission denied. Switching to text input fallback.");
        });
    }
  }

  stopRecording() {
    this.isRecording = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }

    return new Promise((resolve) => {
      if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
          resolve(audioBlob);
        };
        this.mediaRecorder.stop();
        // Stop stream tracks
        if (this.mediaRecorder.stream) {
          this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
      } else {
        resolve(null);
      }
    });
  }
}

window.voiceService = new VoiceService();

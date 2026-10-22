// Cyber Audio Synthesizer (Web Audio API)
class CyberAudioEngine {
  constructor() {
    this.ctx = null;
    this.muted = false;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    return this.muted;
  }

  playTone(freq, type = 'sine', duration = 0.15, gainVal = 0.2, rampDown = true) {
    if (this.muted) return;
    try {
      this.init();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      if (rampDown) {
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);
      }

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn("Audio error:", e);
    }
  }

  playJoin() {
    this.init();
    // High tech warp chord
    this.playTone(523.25, 'sine', 0.12, 0.25);
    setTimeout(() => this.playTone(659.25, 'sine', 0.15, 0.25), 60);
    setTimeout(() => this.playTone(783.99, 'triangle', 0.25, 0.3), 120);
  }

  playOrderSnap() {
    this.init();
    // Mechanical click snap
    this.playTone(880, 'square', 0.05, 0.15);
    setTimeout(() => this.playTone(1760, 'sine', 0.04, 0.1), 30);
  }

  playTick(remaining) {
    this.init();
    if (remaining <= 5) {
      // Urgent tension beep
      this.playTone(880 + (5 - remaining) * 80, 'sawtooth', 0.08, 0.2);
    } else {
      // Normal soft digital tick
      this.playTone(440, 'triangle', 0.04, 0.1);
    }
  }

  playCorrect() {
    this.init();
    // Cyber victory chord: C5 -> E5 -> G5 -> C6
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'sine', 0.3, 0.25);
      }, idx * 70);
    });
  }

  playWrong() {
    this.init();
    // Dissonant cyber error
    this.playTone(220, 'sawtooth', 0.25, 0.3);
    setTimeout(() => this.playTone(196, 'sawtooth', 0.35, 0.3), 100);
  }

  playPodium() {
    this.init();
    // Grand cyber fanfare
    const chords = [
      [523.25, 659.25, 783.99],
      [587.33, 739.99, 880.00],
      [659.25, 830.61, 987.77],
      [783.99, 987.77, 1174.66, 1567.98]
    ];
    chords.forEach((chord, step) => {
      setTimeout(() => {
        chord.forEach(f => this.playTone(f, 'triangle', 0.45, 0.2));
      }, step * 240);
    });
  }
}

const cyberAudio = new CyberAudioEngine();

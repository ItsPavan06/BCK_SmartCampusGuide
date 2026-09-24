/**
 * app.js
 * ------
 * Frontend controller for Bhandarkars' Arts & Science College Smart Help Desk.
 * 
 * Features:
 * 1. Web Speech API (zero-latency speech recognition directly in browser)
 * 2. REST API Integration (/api/query, /api/iot/status, /api/voice-listen)
 * 3. Dynamic results rendering (Dijkstra navigation steps, campus DB details)
 * 4. Text-to-Speech voice responses (browser SpeechSynthesis)
 * 5. IoT PIR Motion Sensor auto-welcome polling
 */

// Timing constants
const transitionDuration = 340;
let resultsAutoReturnTimer = null;
let speechRecognizer = null;
let currentSpeechUtterance = null;
let resultSpeechTimer = null;

// DOM Elements
const clock = document.querySelector('#clock');
const iotStatusBadge = document.querySelector('#iot-status-badge');
const startButton = document.querySelector('.start-listening');
const stopButton = document.querySelector('.stop-listening');
const askAgainButton = document.querySelector('.ask-again');
const replaySpeechButton = document.querySelector('#replay-speech-btn');
const kioskForm = document.querySelector('#kiosk-query-form');
const manualInput = document.querySelector('#manual-query-input');
const liveSpeechEl = document.querySelector('#live-speech');
const toggleRouteBtn = document.querySelector('#toggle-route-btn');
const routeStepsDrawer = document.querySelector('#route-steps-drawer');
const triggerServerMicBtn = document.querySelector('.trigger-server-mic');


// -------------------------------------------------------------
// NAVIGATION & PAGE TRANSITIONS
// -------------------------------------------------------------

function navigateTo(destination) {
  // Cancel active speech when navigating
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  document.body.classList.add('page-leaving');
  window.setTimeout(() => {
    window.location.href = destination;
  }, transitionDuration);
}

function beginListening() {
  navigateTo('listening.html');
}


// -------------------------------------------------------------
// CLOCK
// -------------------------------------------------------------

function updateClock() {
  if (!clock) return;
  const now = new Date();
  clock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}


// -------------------------------------------------------------
// TEXT-TO-SPEECH (TTS)
// -------------------------------------------------------------

function getPreferredSpeechVoice() {
  const voices = window.speechSynthesis.getVoices();
  if (!voices || !voices.length) return null;

  const preferredPatterns = [
    /samantha/i,
    /zira/i,
    /google us english/i,
    /google uk english/i,
    /google english/i,
    /india/i,
    /indian/i,
    /hindi/i,
    /english india/i,
    /en-in/i,
    /en-us/i,
    /en-gb/i,
    /natural/i,
    /aria/i,
    /olivia/i,
    /jenny/i,
    /emma/i,
    /daniel/i,
    /english/i
  ];

  const englishVoices = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith('en'));
  const indianVoices = englishVoices.filter(v => {
    const name = (v.name || '').toLowerCase();
    const lang = (v.lang || '').toLowerCase();
    return name.includes('india') || name.includes('indian') || lang.includes('en-in') || lang.includes('en_in');
  });

  const matchedVoice = indianVoices.find(v => preferredPatterns.some(pattern => pattern.test(v.name)))
    || indianVoices[0]
    || englishVoices.find(v => preferredPatterns.some(pattern => pattern.test(v.name)))
    || englishVoices[0]
    || voices[0]
    || null;

  return matchedVoice;
}

function speakText(text) {
  if (!('speechSynthesis' in window) || !text) return;

  const cleanText = String(text).replace(/\s+/g, ' ').trim();
  if (!cleanText) return;

  window.speechSynthesis.cancel();

  const speakWithPreferredVoice = () => {
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const preferredVoice = getPreferredSpeechVoice();

    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1;
    utterance.lang = 'en-US';

    utterance.text = cleanText;

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    currentSpeechUtterance = utterance;

    // Chrome keepalive for long speech synthesis
    let keepAliveTimer = setInterval(() => {
      if (!window.speechSynthesis || !window.speechSynthesis.speaking) {
        clearInterval(keepAliveTimer);
      } else {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      }
    }, 10000);

    utterance.onend = () => {
      clearInterval(keepAliveTimer);
      currentSpeechUtterance = null;
    };
    utterance.onerror = () => {
      clearInterval(keepAliveTimer);
      currentSpeechUtterance = null;
    };

    window.speechSynthesis.speak(utterance);
  };

  const voices = window.speechSynthesis.getVoices();
  if (voices && voices.length) {
    speakWithPreferredVoice();
    return;
  }

  let attempts = 0;
  const waitForVoices = () => {
    const readyVoices = window.speechSynthesis.getVoices();
    if (readyVoices && readyVoices.length) {
      speakWithPreferredVoice();
      return;
    }

    attempts += 1;
    if (attempts < 20) {
      window.setTimeout(waitForVoices, 200);
    } else {
      speakWithPreferredVoice();
    }
  };

  waitForVoices();
}


// -------------------------------------------------------------
// API CLIENT & QUERY SUBMISSION
// -------------------------------------------------------------

async function submitQuery(queryText, origin = null) {
  if (!queryText || !queryText.trim()) return;
  const cleanQuery = queryText.trim();
  sessionStorage.setItem('wayfinderQuery', cleanQuery);

  if (liveSpeechEl) {
    liveSpeechEl.textContent = 'Processing: "' + cleanQuery + '"...';
  }

  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: cleanQuery, origin: origin })
    });

    if (response.ok) {
      const data = await response.json();
      sessionStorage.setItem('kioskResponse', JSON.stringify(data));
      navigateTo('results.html');
      return;
    }
  } catch (err) {
    console.warn('API query failed, falling back to local fallback:', err);
  }

  // Fallback response if server is unreachable
  const fallback = {
    status: 'success',
    query: cleanQuery,
    intent: 'navigation',
    speech_text: 'Directions for ' + cleanQuery + ' can be obtained at the main college office in Admin Block.',
    primary_result: {
      title: cleanQuery,
      subtitle: 'Campus Landmark',
      description: 'Campus information and assistance available at the Admin Block help desk.',
      walk_time: '1 min',
      distance: '50m',
      status_badge: 'LOCATION',
      floor_info: 'Campus Map',
      hours: 'Mon-Sat 8:30 AM - 6:00 PM',
      steps: ['Step 1: Head towards Admin Block lobby.', 'Step 2: Check with staff at the help desk.']
    },
    secondary_result: {
      title: 'Central Library',
      location: 'Block B · 2nd Floor',
      details: 'Study tables and books available for all students.',
      walk_time: '2 min',
      tag: 'RECOMMENDED'
    }
  };
  sessionStorage.setItem('kioskResponse', JSON.stringify(fallback));
  navigateTo('results.html');
}


// -------------------------------------------------------------
// IOT PIR SENSOR POLLING
// -------------------------------------------------------------

async function pollIoTStatus() {
  try {
    const res = await fetch('/api/iot/status');
    if (res.ok) {
      const iot = await res.json();
      if (iotStatusBadge) {
        if (iot.state === 'WELCOME') {
          iotStatusBadge.textContent = 'Visitor Detected';
          iotStatusBadge.classList.add('iot-active-badge');
        } else if (iot.connected) {
          iotStatusBadge.textContent = 'PIR Connected';
          iotStatusBadge.classList.remove('iot-active-badge');
        } else {
          iotStatusBadge.textContent = 'Campus guide';
          iotStatusBadge.classList.remove('iot-active-badge');
        }
      }

      // If a visitor arrives on the home screen, greet them
      if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/')) {
        if (iot.state === 'WELCOME' && !sessionStorage.getItem('greetedVisitor')) {
          sessionStorage.setItem('greetedVisitor', 'true');
          speakText("Welcome to Bhandarkars' Arts and Science College. How can I help you today?");
          window.setTimeout(() => {
            sessionStorage.removeItem('greetedVisitor');
          }, 15000);
        }
      }
    }
  } catch (e) {
    // Backend offline or running standalone
  }
}


// -------------------------------------------------------------
// PAGE: LISTENING (Speech Recognition & Text Fallback)
// -------------------------------------------------------------

function initListeningPage() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRecognition) {
    try {
      speechRecognizer = new SpeechRecognition();
      speechRecognizer.continuous = false;
      speechRecognizer.interimResults = true;
      speechRecognizer.lang = 'en-US';

      speechRecognizer.onstart = () => {
        if (liveSpeechEl) liveSpeechEl.textContent = 'Listening... Speak now.';
      };

      speechRecognizer.onresult = (event) => {
        let interimText = '';
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalText += event.results[i][0].transcript;
          } else {
            interimText += event.results[i][0].transcript;
          }
        }

        if (liveSpeechEl) {
          liveSpeechEl.textContent = finalText || interimText;
        }

        if (finalText && finalText.trim()) {
          speechRecognizer.stop();
          submitQuery(finalText.trim());
        }
      };

      speechRecognizer.onerror = (event) => {
        console.warn('Speech recognition notice:', event.error);
        if (liveSpeechEl && event.error === 'not-allowed') {
          liveSpeechEl.textContent = 'Microphone permission blocked. Please type your query below.';
        }
      };

      speechRecognizer.start();
    } catch (e) {
      console.warn('SpeechRecognition initialization error:', e);
    }
  } else {
    if (liveSpeechEl) {
      liveSpeechEl.textContent = 'Browser speech recognition unavailable. Please type your question below.';
    }
  }

  // Handle Manual Text Query submission
  if (kioskForm) {
    kioskForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (manualInput && manualInput.value.trim()) {
        if (speechRecognizer) {
          try { speechRecognizer.stop(); } catch (_) {}
        }
        submitQuery(manualInput.value.trim());
      }
    });
  }

  // Handle Server Hardware Mic button (calls /api/voice-listen)
  if (triggerServerMicBtn) {
    triggerServerMicBtn.addEventListener('click', async () => {
      if (liveSpeechEl) liveSpeechEl.textContent = 'Recording via Kiosk Microphone...';
      try {
        const res = await fetch('/api/voice-listen', { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          if (data.recognized_text) {
            sessionStorage.setItem('kioskResponse', JSON.stringify(data));
            sessionStorage.setItem('wayfinderQuery', data.recognized_text);
            navigateTo('results.html');
            return;
          } else if (data.message) {
            if (liveSpeechEl) liveSpeechEl.textContent = data.message;
            return;
          }
        }
      } catch (err) {
        if (liveSpeechEl) liveSpeechEl.textContent = 'Kiosk mic request failed. Type your query below.';
      }
    });
  }
}


// -------------------------------------------------------------
// PAGE: RESULTS (Dynamic Card Rendering & Turn Directions)
// -------------------------------------------------------------

function initResultsPage() {
  const queryTextEl = document.querySelector('#query-text');
  const targetSubjectEl = document.querySelector('#target-subject');
  const primaryTagEl = document.querySelector('#primary-tag');
  const primaryTitleEl = document.querySelector('#primary-title');
  const primaryDescEl = document.querySelector('#primary-description');
  const primaryWalkTimeEl = document.querySelector('#primary-walk-time');
  const primaryDistEl = document.querySelector('#primary-distance');
  const primaryHoursEl = document.querySelector('#primary-hours');

  const secondaryTagEl = document.querySelector('#secondary-tag');
  const secondaryTitleEl = document.querySelector('#secondary-title');
  const secondaryDescEl = document.querySelector('#secondary-description');
  const secondaryWalkTimeEl = document.querySelector('#secondary-walk-time');
  const secondaryActionBtn = document.querySelector('#secondary-action-btn');

  // Load stored query and response
  const heardQuery = sessionStorage.getItem('wayfinderQuery') || 'Where is the library?';
  if (queryTextEl) queryTextEl.textContent = heardQuery;

  const rawData = sessionStorage.getItem('kioskResponse');
  let data = null;
  if (rawData) {
    try { data = JSON.parse(rawData); } catch (_) {}
  }

  if (data && data.primary_result) {
    const p = data.primary_result;
    const steps = p.steps || (data.navigation_details && data.navigation_details.steps) || [];
    const description = p.description || p.subtitle || '';
    const isGenericUnderstandingMessage = /could not understand your question|please ask about campus locations/i.test(description);
    const displayDescription = isGenericUnderstandingMessage
      ? (p.subtitle || steps.join(' ') || 'Campus destination details unavailable.')
      : description;

    if (targetSubjectEl) targetSubjectEl.textContent = p.title || 'Result';
    if (primaryTagEl) primaryTagEl.textContent = p.status_badge || 'BEST MATCH';
    if (primaryTitleEl) primaryTitleEl.textContent = p.title || 'Campus Destination';
    if (primaryDescEl) primaryDescEl.textContent = displayDescription;
    if (primaryWalkTimeEl) primaryWalkTimeEl.textContent = p.walk_time || '1 min';
    if (primaryDistEl) primaryDistEl.textContent = p.distance ? `${p.distance} walk` : 'on campus';
    if (primaryHoursEl) primaryHoursEl.textContent = p.hours || 'Working hours: 8:30 AM - 5:15 PM';

    // Populate turn-by-turn route steps if available
    if (steps.length > 0 && routeStepsDrawer && toggleRouteBtn) {
      routeStepsDrawer.innerHTML = '';
      steps.forEach((step, idx) => {
        const item = document.createElement('div');
        item.className = 'route-step-item';
        item.innerHTML = `<span class="step-number">${idx + 1}.</span><span>${step}</span>`;
        routeStepsDrawer.appendChild(item);
      });

      toggleRouteBtn.style.display = 'flex';
      routeStepsDrawer.style.display = 'block';
      toggleRouteBtn.innerHTML = 'Hide turn directions <span>↗</span>';
      toggleRouteBtn.onclick = () => {
        const isHidden = routeStepsDrawer.style.display === 'none';
        routeStepsDrawer.style.display = isHidden ? 'block' : 'none';
        toggleRouteBtn.innerHTML = isHidden ? 'Hide turn directions <span>↗</span>' : 'Show turn-by-turn route <span>↗</span>';
      };
    } else if (toggleRouteBtn) {
      toggleRouteBtn.style.display = 'none';
    }

    // Populate secondary card
    if (data.secondary_result) {
      const s = data.secondary_result;
      if (secondaryTagEl) secondaryTagEl.textContent = s.tag || 'ALSO NEARBY';
      if (secondaryTitleEl) secondaryTitleEl.textContent = s.title || 'Nearby';
      if (secondaryDescEl) secondaryDescEl.textContent = s.details || s.location || '';
      if (secondaryWalkTimeEl) secondaryWalkTimeEl.textContent = s.walk_time || '2 min';

      if (secondaryActionBtn) {
        secondaryActionBtn.onclick = () => {
          submitQuery(`Where is ${s.title}?`);
        };
      }
    }

    // Automatic voice readout of response
    if (data.speech_text) {
      if (resultSpeechTimer) {
        clearTimeout(resultSpeechTimer);
      }

      resultSpeechTimer = window.setTimeout(() => {
        speakText(data.speech_text);
      }, 400);
    }
  }

  // Replay speech button
  if (replaySpeechButton) {
    replaySpeechButton.onclick = () => {
      if (resultSpeechTimer) {
        clearTimeout(resultSpeechTimer);
      }

      if (data && data.speech_text) {
        speakText(data.speech_text);
      }
    };
  }

  // Inactivity timeout: auto-return to home after 45 seconds of idle time
  const resetTimer = () => {
    if (resultsAutoReturnTimer) clearTimeout(resultsAutoReturnTimer);
    resultsAutoReturnTimer = window.setTimeout(() => {
      navigateTo('index.html');
    }, 45000);
  };
  resetTimer();
  document.addEventListener('click', resetTimer);
  document.addEventListener('keydown', resetTimer);
}


// -------------------------------------------------------------
// EVENT LISTENERS & GLOBAL SETUP
// -------------------------------------------------------------

if (startButton) {
  startButton.addEventListener('click', (event) => {
    if (startButton.tagName === 'A') return;
    event.preventDefault();
    beginListening();
  });
}

if (stopButton) {
  stopButton.addEventListener('click', () => {
    if (speechRecognizer) {
      try { speechRecognizer.stop(); } catch (_) {}
    }
    navigateTo('index.html');
  });
}

if (askAgainButton) {
  askAgainButton.addEventListener('click', beginListening);
}

document.querySelectorAll('a[href]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const destination = link.getAttribute('href');
    if (!destination || destination.startsWith('#') || link.target === '_blank') return;
    event.preventDefault();
    navigateTo(destination);
  });
});

document.addEventListener('keydown', (event) => {
  if (event.code === 'Space' && !event.repeat && !event.target.matches('input, textarea, button')) {
    event.preventDefault();
    beginListening();
  }
});

// Integration seam for external callers
window.wayfinderShowResults = (query) => {
  submitQuery(query);
};

// Clock updater
if (clock) {
  updateClock();
  window.setInterval(updateClock, 30000);
}

// IoT Poller
window.setInterval(pollIoTStatus, 3000);
pollIoTStatus();

// Page-specific initialization
const path = window.location.pathname;
if (path.endsWith('listening.html')) {
  initListeningPage();
} else if (path.endsWith('results.html')) {
  initResultsPage();
}

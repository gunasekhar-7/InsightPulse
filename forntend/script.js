/* global Chart */

const API = "http://127.0.0.1:8000";  // Should match your backend port


// Update footer with current API
document.getElementById('apiUrl').textContent = API;

let token = null;

// Helper: querySelector shorthand
const qs = (id) => document.getElementById(id);

// Demo credentials
const DEMO_USER = 'user';
const DEMO_PASS = 'password';

// Service Worker registration
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// Theme toggle
const themeToggle = qs('themeToggle');
themeToggle.onclick = () => {
  document.body.classList.toggle('dark');
  themeToggle.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
};

// Character counter
const textInput = qs('textInput');
const charCounter = qs('charCounter');
textInput.addEventListener('input', () => {
  charCounter.textContent = `${textInput.value.length} characters`;
});

// Demo login
const demoLoginBtn = qs('demoLoginBtn');
demoLoginBtn.onclick = () => {
  qs('user').value = DEMO_USER;
  qs('pass').value = DEMO_PASS;
};

// Focus management and ARIA
const focusFirstInput = (sectionId) => {
  const section = qs(sectionId);
  const firstInput = section.querySelector('input, textarea, button');
  if (firstInput) firstInput.focus();
};

// Login
const loginForm = qs('loginForm');
loginForm.onsubmit = async (e) => {
  e.preventDefault();
  qs('authError').textContent = '';
  const username = qs('user').value.trim();
  const password = qs('pass').value.trim();
  try {
    const resp = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!resp.ok) throw new Error((await resp.json()).detail || 'Login failed');
    token = (await resp.json()).access_token;
    qs('authSection').classList.add('hidden');
    qs('analysisSection').classList.remove('hidden');
    // Optionally store token in localStorage for session persistence
    // localStorage.setItem('token', token);
    focusFirstInput('analysisSection');
  } catch (err) {
    qs('authError').textContent = err.message;
    focusFirstInput('authSection');
  }
};

// Logout
const logoutBtn = document.createElement('button');
logoutBtn.className = 'btn';
logoutBtn.textContent = 'Logout';
logoutBtn.onclick = () => {
  token = null;
  // localStorage.removeItem('token');
  qs('authSection').classList.remove('hidden');
  qs('analysisSection').classList.add('hidden');
  focusFirstInput('authSection');
};
qs('analysisSection').prepend(logoutBtn);

// Example text
const exampleButton = qs('exampleButton');
exampleButton.onclick = () => {
  qs('textInput').value = 'The staff were professional, but the food was average. Would visit again for the service!';
  charCounter.textContent = `${qs('textInput').value.length} characters`;
  qs('textInput').focus();
};

// Analyze sentiment
const analyzeForm = qs('analyzeForm');
analyzeForm.onsubmit = async (e) => {
  e.preventDefault();
  qs('errorMsg').textContent = '';
  qs('loading').style.display = 'block';
  const text = qs('textInput').value.trim();
  if (!text) {
    qs('errorMsg').textContent = 'Please enter some text';
    qs('loading').style.display = 'none';
    return;
  }
  try {
    const resp = await fetch(`${API}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    });
    if (!resp.ok) throw new Error((await resp.json()).detail || 'Analysis failed');
    const data = await resp.json();
    renderResult(data);
  } catch (err) {
    let msg = err.message;
    if (err.message.includes('Failed to fetch')) {
      msg = 'Network error. Please check your connection.';
      // Optionally show retry button
    }
    qs('errorMsg').textContent = msg;
    focusFirstInput('analysisSection');
  } finally {
    qs('loading').style.display = 'none';
  }
};

// Result rendering
let chart = null;

function getSentimentEmoji(sentiment) {
  return {
    positive: '😊',
    negative: '😞',
    neutral: '😐'
  }[sentiment] || '';
}

function renderResult({ sentiment, probabilities, cleaned_text }) {
  qs('overallSentiment').textContent = sentiment.toUpperCase();
  qs('sentimentEmoji').textContent = getSentimentEmoji(sentiment);
  qs('cleanedText').textContent = cleaned_text;

  const labels = ['positive', 'negative', 'neutral'].map(x => x[0].toUpperCase() + x.slice(1));
  const vals = labels.map(l => probabilities ? probabilities[l.toLowerCase()] || 0 : 0);

  if (chart) chart.destroy();
  chart = new Chart(qs('sentimentChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: vals,
        backgroundColor: ['var(--positive)', 'var(--negative)', 'var(--neutral)']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });

  qs('resultsContainer').classList.remove('hidden');
  focusFirstInput('resultsContainer');
}

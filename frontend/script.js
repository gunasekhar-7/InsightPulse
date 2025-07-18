// InsightPulse/frontend/script.js

const textInput = document.getElementById('textInput');
const analyzeButton = document.getElementById('analyzeButton');
const overallSentimentDisplay = document.getElementById('overallSentiment');
const sentimentIcon = document.getElementById('sentimentIcon');
const resultsContainer = document.getElementById('resultsContainer');
const errorContainer = document.getElementById('errorContainer');
const loadingIndicator = document.getElementById('loadingIndicator');
const cleanedTextDisplay = document.getElementById('cleanedTextDisplay');
const displayCleanedText = document.getElementById('displayCleanedText');
const chartCtx = document.getElementById('sentimentChart').getContext('2d');
const exampleButton = document.getElementById('exampleButton');
const themeToggle = document.getElementById('themeToggle');

// Theme toggle (dark/light mode)
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  themeToggle.textContent = document.body.classList.contains('dark-mode') ? "☀️" : "🌙";
});

exampleButton.addEventListener('click', () => {
  textInput.value = "The staff were professional, but the food was average. Would visit again for the service!";
});

// Dynamic API URL (production/dev support)
let apiBaseUrl = "http://127.0.0.1:5000";
if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
  // Example production switch, customize as needed
  apiBaseUrl = "https://your-deployed-api.example.com";
}

let sentimentChart;

function initializeChart(labels, data) {
  if (sentimentChart) sentimentChart.destroy();
  sentimentChart = new Chart(chartCtx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Sentiment Probability',
        data: data,
        backgroundColor: [
          'rgba(46, 204, 113, 0.7)',
          'rgba(231, 76, 60, 0.7)',
          'rgba(243, 156, 18, 0.7)'
        ],
        borderColor: [
          'rgba(46, 204, 113, 1)',
          'rgba(231, 76, 60, 1)',
          'rgba(243, 156, 18, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) label += ': ';
              if (context.parsed.y !== null) {
                label += context.parsed.y + '%';
              }
              return label;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: { display: true, text: 'Probability (%)' }
        },
        x: { title: { display: true, text: 'Sentiment' } }
      }
    }
  });
}

analyzeButton.addEventListener('click', async () => {
  const text = textInput.value.trim();
  if (!text) {
    errorContainer.textContent = 'Please enter some text to analyze.';
    errorContainer.style.display = 'block';
    resultsContainer.style.display = 'none';
    cleanedTextDisplay.style.display = 'none';
    return;
  }
  errorContainer.style.display = 'none';
  loadingIndicator.classList.add('active');
  analyzeButton.disabled = true;
  resultsContainer.style.display = 'none';
  cleanedTextDisplay.style.display = 'none';
  try {
    const response = await fetch(`${apiBaseUrl}/analyze_sentiment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text }),
    });
    if (!response.ok) {
      let errorMsg = `Error ${response.status}`;
      try { errorMsg = (await response.json()).error || errorMsg; } catch {}
      throw new Error(errorMsg);
    }
    const data = await response.json();
    overallSentimentDisplay.textContent = data.sentiment;
    resultsContainer.classList.remove('positive', 'negative', 'neutral');
    overallSentimentDisplay.classList.remove('positive', 'negative', 'neutral');
    sentimentIcon.className = 'fas';
    if (data.sentiment === 'positive') {
      overallSentimentDisplay.classList.add('positive');
      resultsContainer.classList.add('positive');
      sentimentIcon.classList.add('fa-smile');
    } else if (data.sentiment === 'negative') {
      overallSentimentDisplay.classList.add('negative');
      resultsContainer.classList.add('negative');
      sentimentIcon.classList.add('fa-frown');
    } else {
      overallSentimentDisplay.classList.add('neutral');
      resultsContainer.classList.add('neutral');
      sentimentIcon.classList.add('fa-meh');
    }
    const labels = Object.keys(data.probabilities);
    const values = Object.values(data.probabilities);
    initializeChart(labels, values);
    displayCleanedText.textContent = data.cleaned_text || 'No cleaned text available.';
    cleanedTextDisplay.style.display = 'block';
    resultsContainer.style.display = 'grid';
  } catch (error) {
    errorContainer.textContent = `Analysis failed: ${error.message}`;
    errorContainer.style.display = 'block';
  } finally {
    loadingIndicator.classList.remove('active');
    analyzeButton.disabled = false;
  }
});

// Hide results & cleaned text by default
resultsContainer.style.display = 'none';
cleanedTextDisplay.style.display = 'none';

document.addEventListener('DOMContentLoaded', function() {
    
    // --- PART 0: INITIALIZATION ---
    const dateInput = document.getElementById('logDate');
    if (dateInput) {
        dateInput.valueAsDate = new Date();
    }
    
    // --- PART 1: CHART & TOGGLE LOGIC (Kept exactly as is) ---
    const toggleBtn = document.getElementById('toggleViewBtn');
    const listView = document.getElementById('historyList');
    const graphView = document.getElementById('historyGraph');
    let isGraphMode = false;
    let charts = {}; 

    function renderAllCharts() {
        if (typeof chartData === 'undefined' || chartData.length === 0) return;
        const data = [...chartData].reverse();
        const labels = data.map(log => {
            const d = new Date(log.log_date);
            return `${d.getDate()}/${d.getMonth()+1}`;
        });

        const createChart = (canvasId, label, datasetData, color, type='line') => {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return; 
            const ctx = canvas.getContext('2d');
            if (charts[canvasId]) charts[canvasId].destroy(); 

            charts[canvasId] = new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: datasetData,
                        borderColor: color,
                        backgroundColor: color + '33',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        };

        createChart('chartDuration', 'Duration (hrs)', data.map(d => d.sleep_duration), '#3498db');
        createChart('chartQuality', 'Quality (1-10)', data.map(d => d.quality_sleep), '#9b59b6');
        createChart('chartStress', 'Stress (1-10)', data.map(d => d.stress_level), '#e74c3c');
        createChart('chartHR', 'Heart Rate (bpm)', data.map(d => d.heart_rate), '#e91e63');

        const bpCanvas = document.getElementById('chartBP');
        if (bpCanvas) {
            const ctxBP = bpCanvas.getContext('2d');
            if (charts['chartBP']) charts['chartBP'].destroy();
            charts['chartBP'] = new Chart(ctxBP, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Systolic', data: data.map(d => d.bp_systolic), borderColor: '#e67e22', fill: false },
                        { label: 'Diastolic', data: data.map(d => d.bp_diastolic), borderColor: '#2ecc71', fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        const actCanvas = document.getElementById('chartActivity');
        if (actCanvas) {
            const ctxAct = actCanvas.getContext('2d');
            if (charts['chartActivity']) charts['chartActivity'].destroy();
            charts['chartActivity'] = new Chart(ctxAct, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Activity (mins)',
                            data: data.map(d => d.activity_level),
                            backgroundColor: '#34495e',
                            order: 2,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Steps',
                            data: data.map(d => d.daily_steps),
                            borderColor: '#1abc9c',
                            backgroundColor: 'rgba(26, 188, 156, 0.1)',
                            type: 'line',
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 4,
                            order: 1,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: { 
                    responsive: true, maintainAspectRatio: false,
                    scales: {
                        y: { position: 'left', title: {display: true, text: 'Mins'}, beginAtZero: true },
                        y1: { position: 'right', title: {display: true, text: 'Steps'}, grid: {drawOnChartArea: false}, beginAtZero: true }
                    }
                }
            });
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            isGraphMode = !isGraphMode;
            if (isGraphMode) {
                listView.style.display = 'none';
                graphView.style.display = 'block';
                toggleBtn.innerHTML = '<i class="fas fa-list"></i> View List';
                graphView.classList.remove('hidden'); 
                renderAllCharts();
            } else {
                listView.style.display = 'block';
                graphView.style.display = 'none';
                toggleBtn.innerHTML = '<i class="fas fa-chart-line"></i> View Graphs';
            }
        });
    }

 // --- PART 2: FORM SUBMISSION LOGIC ---
    const form = document.getElementById('predictionForm');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); 

            // 1. Gather Data
            const data = {
                date: document.getElementById('logDate').value,
                gender: parseInt(document.getElementById('gender').value),
                age: parseInt(document.getElementById('age').value),
                duration: parseFloat(document.getElementById('duration').value),
                quality: parseInt(document.getElementById('quality').value),
                activity: parseInt(document.getElementById('activity').value),
                stress: parseInt(document.getElementById('stress').value),
                bmi: parseInt(document.getElementById('bmi').value),
                bp_sys: parseInt(document.getElementById('bp_sys').value),
                bp_dia: parseInt(document.getElementById('bp_dia').value),
                heart_rate: parseInt(document.getElementById('heart_rate').value),
                daily_steps: parseInt(document.getElementById('daily_steps').value)
            };

            try {
                const response = await fetch('/submit_log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    // 1. POPUP SUCCESS MESSAGE
                    alert("The log has been saved successfully!");
                
                    const sleepTipBox = document.getElementById('sleepTipBox');
                    const sleepTipText = document.getElementById('sleepTipText');
                    const resultBox = document.getElementById('resultBox');
                    const resultText = document.getElementById('predictionResult');
                    const weeklyAdvice = document.getElementById('weeklyAdvice');

                    // 2. Logic: Decide what to show
                    if (sleepTipBox) {
                        // Always show the Blue Box first (for status/advice)
                        sleepTipBox.classList.remove('hidden');

                        if (result.weekly_ready) {
                            // === SCENARIO A: 7th Day (Report Ready) ===
                            
                            // Pink Box: Show the AI ADVICE
                            if (sleepTipText) sleepTipText.innerText = result.analysis.tips;

                            // Green Box: Show the PREDICTION
                            if (resultBox) {
                                resultBox.classList.remove('hidden');
                                if (resultText) resultText.innerText = result.analysis.prediction;
                                if (weeklyAdvice) weeklyAdvice.innerText = "Detailed advice is in the Pink Box above.";
                            }

                        } else {
                            // === SCENARIO B: Days 1-6 (Normal Day) ===
                            
                            // Pink Box Message
                            if (sleepTipText) {
                                sleepTipText.innerHTML = "Keep logging! We need 7 days of data to generate your weekly sleep tips.";
                            }
                        
                            // Green Box Message
                            if (resultBox) {
                                resultBox.classList.remove('hidden');
                                if (resultText) resultText.innerHTML = "Keep logging! We need 7 days of data to generate your weekly prediction.";
                                if (weeklyAdvice) weeklyAdvice.innerText = "";
                            }
                        } 

                        // Scroll to the result so user sees it
                        sleepTipBox.scrollIntoView({ behavior: 'smooth' });
                    }

                } else {
                    alert("Error saving log: " + (result.error || "Unknown error"));
                }
            } catch (error) {
                console.error("Connection Error:", error);
                alert("Failed to connect to server.");
            }
        });
    }
    });
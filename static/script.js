document.addEventListener('DOMContentLoaded', function() {
    
    // --- PART 1: CHART & TOGGLE LOGIC ---
    const toggleBtn = document.getElementById('toggleViewBtn');
    const listView = document.getElementById('historyList');
    const graphView = document.getElementById('historyGraph');
    let isGraphMode = false;
    let charts = {}; // Store Chart Instances

    // Function to Draw All Charts
    function renderAllCharts() {
        if (typeof chartData === 'undefined' || chartData.length === 0) return;

        // Prepare Data (Sort Oldest -> Newest)
        const data = [...chartData].reverse();
        const labels = data.map(log => {
            const d = new Date(log.log_date);
            return `${d.getDate()}/${d.getMonth()+1}`;
        });

        // Helper to create a chart
        const createChart = (canvasId, label, datasetData, color, type='line') => {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return; // Safety check
            
            const ctx = canvas.getContext('2d');
            if (charts[canvasId]) charts[canvasId].destroy(); // Destroy old chart

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

        // 1. Sleep Duration (Blue)
        createChart('chartDuration', 'Duration (hrs)', data.map(d => d.sleep_duration), '#3498db');
        // 2. Sleep Quality (Purple)
        createChart('chartQuality', 'Quality (1-10)', data.map(d => d.quality_sleep), '#9b59b6');
        // 3. Stress Level (Red)
        createChart('chartStress', 'Stress (1-10)', data.map(d => d.stress_level), '#e74c3c');
        // 4. Heart Rate (Pink)
        createChart('chartHR', 'Heart Rate (bpm)', data.map(d => d.heart_rate), '#e91e63');

        // 5. Blood Pressure (Double Line)
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

        // 6. Activity vs Steps (Mixed)
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

    // Toggle Button Event Listener
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            isGraphMode = !isGraphMode;
            if (isGraphMode) {
                listView.style.display = 'none';
                graphView.style.display = 'block';
                toggleBtn.innerHTML = '<i class="fas fa-list"></i> View List';
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
            e.preventDefault(); // Stop page reload

            // 1. Gather Data
            const data = {
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
                // 2. Send to Python
                const response = await fetch('/submit_log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    // 3. Show Daily Tip
                    const tipBox = document.getElementById('dailyTipBox');
                    if (tipBox) {
                        tipBox.classList.remove('hidden');
                        document.getElementById('dailyTipText').innerText = result.daily_tip;
                        tipBox.scrollIntoView({ behavior: 'smooth' });
                    }

                    // 4. Show Weekly Analysis (if ready)
                    if (result.weekly_ready) {
                        const weeklyBox = document.getElementById('weeklyBox');
                        if (weeklyBox) {
                            weeklyBox.classList.remove('hidden');
                            document.getElementById('predictionResult').innerText = result.analysis.prediction;
                            document.getElementById('weeklyAdvice').innerText = result.analysis.tips;
                        }
                    }

                    // 5. Clear form slightly to show success (optional)
                    // form.reset(); 
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
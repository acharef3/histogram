async function loadHistogram() {
            try {
                // Fetch data from the Python backend
                const response = await fetch('/histogram-data');
                const data = await response.json();

                if (data.error) {
                    console.error("Error loading histogram data:", data.error);
                    return;
                }

                // Render Chart.js Graph
                const ctx = document.getElementById('histogramChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels, // X-Axis: Dates of the scenes
                        datasets: [{
                            label: 'Amount of Frames Recorded',
                            data: data.values, // Y-Axis: Amount of frames
                            backgroundColor: 'rgba(59, 130, 246, 0.7)', // Raytheon Blue
                            borderColor: 'rgba(59, 130, 246, 1)',
                            borderWidth: 1,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { 
                                    display: true, 
                                    text: 'Amount of Frames', 
                                    font: { weight: 'bold' } 
                                }
                            },
                            x: {
                                title: { 
                                    display: true, 
                                    text: 'Date of Scene', 
                                    font: { weight: 'bold' } 
                                }
                            }
                        }
                    }
                });
            } catch (err) {
                console.error("Failed to load histogram:", err);
            }
        }

        // Run Histogram Visualization
        loadHistogram();

    </script>

    <script src="{{ url_for('static', filename='scripts/Gazetteer.js') }}"></script>

</body>
</html>

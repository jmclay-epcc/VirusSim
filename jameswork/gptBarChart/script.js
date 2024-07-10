const ctx = document.getElementById('myChart').getContext('2d');
let dataValues = [];
let labels = [];

// Initialize the chart
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: '# of Values',
            data: dataValues,
            backgroundColor: 'rgba(75, 192, 192)',
            barPercentage: 1.0,       // Make bars full width
            categoryPercentage: 1.0 
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Function to generate a new value
function generateNewValue() {
    const newValue = Math.floor(Math.random() * 100); // Random value between 0 and 99
    dataValues.push(newValue);
    labels.push(labels.length + 1); // Use index as label

    console.log('New Value:', newValue); // Debugging: log new value
    console.log('Data Values:', dataValues); // Debugging: log data array

    myChart.update();
}

// Generate a new value every second
setInterval(generateNewValue, 1000);

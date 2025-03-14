let intervalId;

async function authenticate() {
    //const ipAddress = document.getElementById('ipAddress').value;
    //const username = document.getElementById('username').value;
    //const password = document.getElementById('password').value;
    
    //EDGE_IP = "10.164.195.223"

    //auth_details = {
    //    "username": "so",
    //    "password": "Emerson1!"
    //}

    const ipAddress =  "10.164.195.223"
    const username = "so"
    const password = "Emerson1!"
    
    const response = await fetch('/authenticate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `ipAddress=${encodeURIComponent(ipAddress)}&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });

    const result = await response.json();
    handleAuthenticationResult(response.status, result);
}

function handleAuthenticationResult(status, result) {
    if (status === 200) {
        alert(result.status);
        enableMonitoringSections();
    } else {
        alert(result.status + ": " + result.message);
        disableMonitoringSections();
    }
}

function enableMonitoringSections() {
    document.getElementById('monitor-form').classList.remove('disabled');
    document.getElementById('current-value-container').classList.remove('disabled');
    document.getElementById('history-container').classList.remove('disabled');
}

function disableMonitoringSections() {
    document.getElementById('monitor-form').classList.add('disabled');
    document.getElementById('current-value-container').classList.add('disabled');
    document.getElementById('history-container').classList.add('disabled');
}

async function startMonitoring() {
    //const ipAddress = document.getElementById('ipAddress').value;
    const ipAddress =  "10.164.195.223"
    const path = document.getElementById('path').value;
    const param = document.getElementById('param').value;
    
    const endpoint = `https://${ipAddress}/edge/api/v1/graph?path=${path}&p=${param}`;
    const interval = document.getElementById('interval').value;

    alert("Start monitoring: " + endpoint);

    await fetch('/start_monitoring', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `endpoint=${encodeURIComponent(endpoint)}&interval=${interval}`
    });

    if (intervalId) {
        clearInterval(intervalId);
    }

    intervalId = setInterval(async () => {
        const logResponse = await fetch('/get_log');
        const logData = await logResponse.json();
        updateMonitoringData(logData);
    }, interval * 1000);
}

function updateMonitoringData(logData) {
    const currentValue = logData[logData.length - 1];
    const output = document.getElementById('current-value');
    const historyTable = document.getElementById('history-table').getElementsByTagName('tbody')[0];

    if (currentValue) {
        output.value = JSON.stringify(currentValue.value, null, 2);

        const newRow = historyTable.insertRow();
        newRow.insertCell(0).textContent = currentValue.time;
        newRow.insertCell(1).textContent = JSON.stringify(currentValue.value, null, 2);

        if (historyTable.rows.length > 20) {
            historyTable.deleteRow(0);
        }
    }
}

async function stopMonitoring() {
    if (intervalId) {
        clearInterval(intervalId);
    }
    await fetch('/stop_monitoring', {
        method: 'POST'
    });
}


async function status() {
    const response = await fetch(window.statusURL, {
        method: "POST",
        headers: { "X-CSRFToken": window.csrfToken },
        body: new URLSearchParams({ 'csrfmiddlewaretoken': window.csrfToken, PCStatus: 'status' })
    });

    const data = await response.json();
    const statustext = data.PCStatus;

    for (let i = 1; i < 6; i++) {
        const element = document.getElementById(`status-${i}`);
        if (element && statustext[i-1] !== undefined) {
            element.innerText = statustext[i-1];
        }
    }
}

let previousLog = '';
const logBuffer = Array(10).fill(".");

async function getlog() {
    try {
        const response = await fetch(window.statusURL, {
            method: "POST",
            headers: { 'X-CSRFToken': window.csrfToken },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': window.csrfToken,
                LogKey: 'logkey'
            })
        });
        if (!response.ok) throw new Error("خطا در دریافت لاگ");
        const data = await response.json();
        const currentLog = data.log || '';
        if (currentLog !== previousLog) {
            logBuffer.shift();
            logBuffer.push(currentLog);
            previousLog = currentLog;
        }
        document.getElementById('log').innerText = logBuffer.join('\n');
    } catch (error) {
        console.error(error);
    }
}

async function submitUpdate(event) {
    event.preventDefault();

    const form = document.getElementById("update-form");
    const formData = new FormData(form);

    const submitBtn = form.querySelector('button[type="submit"]');
    const stopBtn = form.querySelector('button[type="button"]');
    const spinner = document.getElementById('spinner');

    submitBtn.disabled = true;
    stopBtn.disabled = true;
    spinner.style.display = 'block';

    try {
        const response = await fetch(window.statusURL, {
            method: "POST",
            headers: { "X-CSRFToken": window.csrfToken },
            body: formData
        });

        const result = await response.json();
        alert(result.status || "Update triggered");
    } catch (error) {
        console.error("Update error:", error);
        alert("خطایی رخ داد.");
    } finally {
        submitBtn.disabled = false;
        stopBtn.disabled = false;
        spinner.style.display = 'none';
    }
}

async function stopTask() {
    const response = await fetch(window.stopURL, {
        method: "POST",
        headers: { "X-CSRFToken": window.csrfToken },
        body: new URLSearchParams({ 'csrfmiddlewaretoken': window.csrfToken, stop: 'stop' })
    });

    const result = await response.json();
    alert(result.status || "Task stopped");
}

document.addEventListener("DOMContentLoaded", () => {
    setInterval(getlog, 1000);
    setInterval(status, 2000);
});
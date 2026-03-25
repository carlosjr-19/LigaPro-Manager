function openShareModal() {
    document.getElementById('shareModal').classList.remove('hidden');
    document.getElementById('shareModal').classList.add('flex');
    toggleDateInputs();
    toggleUpcomingDateInputs();
    if(typeof toggleCurrentMatchdayInput === 'function') { toggleCurrentMatchdayInput(); }
}

function closeShareModal() {
    document.getElementById('shareModal').classList.add('hidden');
    document.getElementById('shareModal').classList.remove('flex');
}

function toggleDateInputs() {
    const isChecked = document.getElementById('check_recent').checked;
    const inputs = document.getElementById('date_inputs');
    if (isChecked) {
        inputs.classList.remove('hidden');
    } else {
        inputs.classList.add('hidden');
    }
}

function toggleUpcomingDateInputs() {
    const isChecked = document.getElementById('check_upcoming')?.checked;
    const inputs = document.getElementById('upcoming_date_inputs');
    if (inputs) {
        if (isChecked) {
            inputs.classList.remove('hidden');
        } else {
            inputs.classList.add('hidden');
        }
    }
}

function toggleCurrentMatchdayInput() {
    const isChecked = document.getElementById('check_current_matchday')?.checked;
    const inputs = document.getElementById('current_matchday_input');
    if (inputs) {
        if (isChecked) {
            inputs.classList.remove('hidden');
        } else {
            inputs.classList.add('hidden');
        }
    }
}

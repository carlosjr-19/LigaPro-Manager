function openShareModal() {
    document.getElementById('shareModal').classList.remove('hidden');
    document.getElementById('shareModal').classList.add('flex');
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

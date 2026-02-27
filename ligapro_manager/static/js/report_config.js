function toggleDateInput(leagueId, isFromStart) {
    const input = document.getElementById('date_input_' + leagueId);
    if (isFromStart) {
        input.classList.add('hidden');
        input.removeAttribute('required');
    } else {
        input.classList.remove('hidden');
        input.setAttribute('required', 'required');
    }
}

function updateHistory(selectId, outputId) {
    const select = document.getElementById(selectId);
    const output = document.getElementById(outputId);
    const teamId = select.value;

    // In JS object keys are always strings. So teamsHistory['1'] works even if key was 1.

    if (!teamId) {
        output.textContent = '';
        return;
    }

    const history = window.teamsHistory[teamId];
    if (!history || Object.keys(history).length === 0) {
        output.textContent = 'Sin partidos previos.';
        return;
    }

    const opponents = [];
    for (const [oppId, count] of Object.entries(history)) {
        const name = window.teamsMap[oppId] || 'Desconocido';
        const countStr = count > 1 ? ` x${count}` : '';
        opponents.push(`${name}${countStr}`);
    }

    output.textContent = 'Ya jugó contra: ' + opponents.join(', ');
}

document.addEventListener('DOMContentLoaded', function () {
    const homeTeamSelect = document.getElementById('home_team_id');
    const awayTeamSelect = document.getElementById('away_team_id');

    if (homeTeamSelect) {
        homeTeamSelect.addEventListener('change', () => updateHistory('home_team_id', 'home_history'));
    }
    if (awayTeamSelect) {
        awayTeamSelect.addEventListener('change', () => updateHistory('away_team_id', 'away_history'));
    }

    // Initial update
    if (homeTeamSelect || awayTeamSelect) {
        updateHistory('home_team_id', 'home_history');
        updateHistory('away_team_id', 'away_history');
    }
});

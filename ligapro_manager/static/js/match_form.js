function updateHistory(selectId, outputId) {
    const select = document.getElementById(selectId);
    const output = document.getElementById(outputId);
    const teamId = select.value;

    if (!teamId) {
        output.textContent = '';
        checkLastEncounter();
        return;
    }

    const history = window.teamsHistory[teamId];
    if (!history || Object.keys(history).length === 0) {
        output.textContent = 'Sin partidos previos.';
        checkLastEncounter();
        return;
    }

    const opponents = [];
    for (const [oppId, data] of Object.entries(history)) {
        const name = window.teamsMap[oppId] || 'Desconocido';
        const count = data.count || 0;
        const countStr = count > 1 ? ` x${count}` : '';
        opponents.push(`${name}${countStr}`);
    }

    output.textContent = 'Ya jugó contra: ' + opponents.join(', ');
    checkLastEncounter();
}

function checkLastEncounter() {
    const homeSelect = document.getElementById('home_team_id');
    const awaySelect = document.getElementById('away_team_id');
    const alertBox = document.getElementById('last_match_alert');
    const dateSpan = document.getElementById('last_match_date');

    if (!homeSelect || !awaySelect || !alertBox || !dateSpan) return;

    const homeId = homeSelect.value;
    const awayId = awaySelect.value;

    if (homeId && awayId && homeId !== awayId) {
        const history = window.teamsHistory[homeId];
        if (history && history[awayId] && history[awayId].last_date) {
            dateSpan.textContent = history[awayId].last_date;
            alertBox.classList.remove('hidden');
            return;
        }
    }
    
    alertBox.classList.add('hidden');
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

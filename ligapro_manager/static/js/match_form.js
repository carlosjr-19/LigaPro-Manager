function updateHistory(selectId, outputId) {
    const select = document.getElementById(selectId);
    const output = document.getElementById(outputId);
    const teamId = select?.value;

    const homeTeamSelect = document.getElementById('home_team_id');
    const awayTeamSelect = document.getElementById('away_team_id');
    
    let otherTeamId = null;
    if (selectId === 'home_team_id' && awayTeamSelect) {
        otherTeamId = awayTeamSelect.value;
    } else if (selectId === 'away_team_id' && homeTeamSelect) {
        otherTeamId = homeTeamSelect.value;
    }

    if (!teamId) {
        output.innerHTML = '';
        checkLastEncounter();
        return;
    }

    const history = window.teamsHistory[teamId];
    if (!history || Object.keys(history).length === 0) {
        output.innerHTML = 'Sin partidos previos.';
        checkLastEncounter();
        return;
    }

    const opponents = [];
    for (const [oppId, data] of Object.entries(history)) {
        // Escape HTML for safety
        const rawName = window.teamsMap[oppId] || 'Desconocido';
        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        const name = escapeHtml(rawName);
        
        const count = data.count || 0;
        const countStr = count > 1 ? ` x${count}` : '';
        const displayText = `${name}${countStr}`;
        
        if (oppId === otherTeamId) {
            opponents.push(`<span class="text-red-400 font-bold bg-red-500/10 px-1 rounded border border-red-500/30">${displayText}</span>`);
        } else {
            opponents.push(displayText);
        }
    }

    output.innerHTML = 'Ya jugó contra: ' + opponents.join(', ');
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
            let text = history[awayId].last_date;
            if (history[awayId].last_time && history[awayId].last_court_name) {
                text += ` - ${history[awayId].last_time} (${history[awayId].last_court_name})`;
            }
            dateSpan.textContent = text;
            alertBox.classList.remove('hidden');
            return;
        }
    }
    
    alertBox.classList.add('hidden');
}

function updateBothHistories() {
    updateHistory('home_team_id', 'home_history');
    updateHistory('away_team_id', 'away_history');
}

document.addEventListener('DOMContentLoaded', function () {
    const homeTeamSelect = document.getElementById('home_team_id');
    const awayTeamSelect = document.getElementById('away_team_id');

    if (homeTeamSelect) {
        homeTeamSelect.addEventListener('change', updateBothHistories);
    }
    if (awayTeamSelect) {
        awayTeamSelect.addEventListener('change', updateBothHistories);
    }

    // Initial update
    if (homeTeamSelect || awayTeamSelect) {
        updateBothHistories();
    }
});

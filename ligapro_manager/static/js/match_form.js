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

    const restData = (window.teamsRests && (window.teamsRests[teamId] || window.teamsRests[parseInt(teamId, 10)])) 
        ? (window.teamsRests[teamId] || window.teamsRests[parseInt(teamId, 10)]) 
        : { count: 0, dates: [] };
    const restCount = restData.count || 0;
    const restDates = restData.dates || [];
    const datesStr = restDates.length > 0 ? `Fechas: ${restDates.join(', ')}` : 'Sin descansos registrados';

    let restBadgeHtml = '';
    if (restCount === 0) {
        restBadgeHtml = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold bg-white/5 text-white/50 border border-white/10" title="${datesStr}"><i class="fas fa-bed text-[10px]"></i> descanso x0</span>`;
    } else {
        restBadgeHtml = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30" title="${datesStr}"><i class="fas fa-bed text-[10px]"></i> descanso x${restCount}</span>`;
    }

    const datesDetailHtml = restDates.length > 0 
        ? `<span class="text-white/40 text-[11px] font-sans">(${restDates.join(', ')})</span>`
        : '';

    const history = window.teamsHistory ? (window.teamsHistory[teamId] || window.teamsHistory[parseInt(teamId, 10)]) : null;
    let opponentsHtml = '';
    if (!history || Object.keys(history).length === 0) {
        opponentsHtml = '<span class="text-white/40 italic">Sin partidos previos.</span>';
    } else {
        const opponents = [];
        for (const [oppId, data] of Object.entries(history)) {
            // Escape HTML for safety
            const rawName = (window.teamsMap && (window.teamsMap[oppId] || window.teamsMap[parseInt(oppId, 10)])) || 'Desconocido';
            const escapeHtml = (text) => {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            };
            const name = escapeHtml(rawName);
            
            const count = data.count || 0;
            const countStr = count > 1 ? ` x${count}` : '';
            const displayText = `${name}${countStr}`;
            
            if (String(oppId) === String(otherTeamId)) {
                opponents.push(`<span class="text-red-400 font-bold bg-red-500/10 px-1 rounded border border-red-500/30">${displayText}</span>`);
            } else {
                opponents.push(displayText);
            }
        }
        opponentsHtml = 'Ya jugó contra: ' + opponents.join(', ');
    }

    output.innerHTML = `
        <div class="flex flex-col gap-1.5 mt-1 font-sans">
            <div class="flex items-center gap-2 flex-wrap">
                ${restBadgeHtml}
                ${datesDetailHtml}
            </div>
            <div class="text-xs text-white/50 leading-relaxed font-mono">
                ${opponentsHtml}
            </div>
        </div>
    `;
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
        const history = window.teamsHistory ? (window.teamsHistory[homeId] || window.teamsHistory[parseInt(homeId, 10)]) : null;
        const awayHistoryData = history ? (history[awayId] || history[parseInt(awayId, 10)]) : null;
        if (awayHistoryData && awayHistoryData.last_date) {
            let text = awayHistoryData.last_date;
            if (awayHistoryData.last_time && awayHistoryData.last_court_name) {
                text += ` - ${awayHistoryData.last_time} (${awayHistoryData.last_court_name})`;
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

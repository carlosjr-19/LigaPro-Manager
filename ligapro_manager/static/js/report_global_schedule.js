function updateMatchScore(matchId, field, value) {
    fetch(window.updateMatchCostsUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({
            match_id: matchId,
            [field]: value
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                alert('Error al guardar resultado: ' + data.error);
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateMatchCost(matchId, field, value, courtId) {
    // Optimistic UI update for totals can be complex, for now we rely on explicit user input.
    // We will just send the data and allow the user to see the value they typed.
    // To update totals immediately, we can parse the DOM inputs for this table.
    recalculateTotals(courtId);

    fetch(window.updateMatchCostsUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({
            match_id: matchId,
            [field]: value
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                alert('Error al guardar: ' + data.error);
            }
        })
        .catch(error => console.error('Error:', error));
}

function recalculateTotals(courtId) {
    // Find the table body associated with this court (we need a way to scope it)
    // Since we didn't add IDs to tbody, let's find the footer and go back to the table
    const footer = document.getElementById('footer-' + courtId);
    if (!footer) return;

    const table = footer.closest('table');
    if (!table) return;

    let sumHome = 0;
    let sumAway = 0;
    let sumReferee = 0;

    // Iterate rows
    const inputs = table.querySelectorAll('input');
    inputs.forEach(input => {
        const val = parseValue(input.value);
        const field = input.getAttribute('data-field');

        if (field === 'referee_cost_home') sumHome += val;
        if (field === 'referee_cost_away') sumAway += val;
        if (field === 'referee_cost') sumReferee += val;
    });

    // Update Footer
    const totalHomeEl = footer.querySelector('[data-type="total-home"]');
    const totalAwayEl = footer.querySelector('[data-type="total-away"]');
    const totalRefereeEl = footer.querySelector('[data-type="total-referee"]');
    const profitEl = footer.querySelector('[data-type="total-profit"]');

    if (totalHomeEl) totalHomeEl.textContent = '$' + sumHome;
    if (totalAwayEl) totalAwayEl.textContent = '$' + sumAway;
    if (totalRefereeEl) totalRefereeEl.textContent = '$' + sumReferee;

    const profit = (sumHome + sumAway) - sumReferee;
    if (profitEl) {
        profitEl.textContent = '$' + profit;
        profitEl.className = profitEl.className.replace(/text-(green|red)-400/, '');
        profitEl.classList.add(profit >= 0 ? 'text-green-400' : 'text-red-400');
    }
}

function parseValue(val) {
    if (!val) return 0;
    // Check for NSP
    if (val.toUpperCase().includes('NSP')) return 0;
    // Try parse
    const num = parseInt(val);
    return isNaN(num) ? 0 : num;
}

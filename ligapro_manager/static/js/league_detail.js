document.addEventListener('DOMContentLoaded', function () {
    const teamSelects = document.querySelectorAll('.team-select');

    teamSelects.forEach(select => {
        select.addEventListener('change', function () {
            const teamId = this.value;
            const targetId = this.dataset.target;
            const playerSelect = document.getElementById(targetId);

            if (playerSelect) {
                playerSelect.innerHTML = '<option value="">Seleccionar Jugador</option>';

                if (teamId && window.playersByTeam && window.playersByTeam[teamId]) {
                    window.playersByTeam[teamId].forEach(player => {
                        const option = document.createElement('option');
                        option.value = player.id; // Send ID to ligapro_manager
                        option.textContent = player.name;
                        playerSelect.appendChild(option);
                    });
                }
            }
        });
    });

    // Initialize tab from URL hash on load
    if (window.location.hash) {
        const tab = window.location.hash.substring(1);
        if (document.getElementById(tab)) {
            showTab(tab);
        }
    }

    // Restore match/playoff preference on load
    const pref = localStorage.getItem('matchView');
    if (pref) {
        toggleMatchView(pref);
    }

    const playoffPref = localStorage.getItem('playoffView');
    if (playoffPref) {
        togglePlayoffView(playoffPref);
    }

    // Toggle highlight settings visibility
    const highlightToggle = document.getElementById('toggle-highlight');
    if (highlightToggle) {
        highlightToggle.addEventListener('change', function () {
            const box = document.getElementById('highlight-settings-box');
            if (this.checked) {
                box.classList.remove('hidden');
            } else {
                box.classList.add('hidden');
            }
        });
    }

    // Validate highlight range
    const hStart = document.getElementById('h-start');
    const hEnd = document.getElementById('h-end');

    if (hStart && hEnd) {
        function validateRange() {
            let start = parseInt(hStart.value);
            let end = parseInt(hEnd.value);

            // Limit checks can be done locally or in backend.
            if (start > end) {
                hStart.value = end;
            }
            if (start < 1) hStart.value = 1;
        }

        hStart.addEventListener('change', validateRange);
        hEnd.addEventListener('change', validateRange);
    }

    // Wire up Delete Button for Matrix
    const btnDeleteMatrix = document.getElementById('btn-delete-matrix-match');
    if (btnDeleteMatrix) {
        btnDeleteMatrix.addEventListener('click', function () {
            const matchId = document.getElementById('matrix_match_id').value;
            if (matchId) {
                document.getElementById('delete_matrix_match_id').value = matchId;
                document.getElementById('deleteMatrixForm').submit();
            }
        });
    }
});

function showTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Show selected tab content
    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {
        selectedContent.classList.add('active');
    }

    // Reset all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Activate selected tab button
    const activeBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    // Update URL hash without jumping
    history.pushState(null, null, `#${tabId}`);
}

function togglePlayoffView(view) {
    const listView = document.getElementById('playoff-list-view');
    const bracketView = document.getElementById('playoff-bracket-view');
    const btnList = document.getElementById('btn-playoff-list');
    const btnBracket = document.getElementById('btn-playoff-bracket');

    if (!listView || !bracketView) return;

    // Reset
    listView.classList.add('hidden');
    bracketView.classList.add('hidden');
    btnList.classList.remove('bg-primary', 'text-white', 'shadow-lg', 'shadow-primary/20');
    btnList.classList.add('text-white/60', 'hover:text-white');
    btnBracket.classList.remove('bg-primary', 'text-white', 'shadow-lg', 'shadow-primary/20');
    btnBracket.classList.add('text-white/60', 'hover:text-white');

    if (view === 'list') {
        listView.classList.remove('hidden');
        btnList.classList.add('bg-primary', 'text-white', 'shadow-lg', 'shadow-primary/20');
        btnList.classList.remove('text-white/60', 'hover:text-white');
    } else {
        bracketView.classList.remove('hidden');
        btnBracket.classList.add('bg-primary', 'text-white', 'shadow-lg', 'shadow-primary/20');
        btnBracket.classList.remove('text-white/60', 'hover:text-white');
    }

    localStorage.setItem('playoffView', view);
}

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

function toggleMatchView(view) {
    const listView = document.getElementById('matches-list-view');
    const matrixView = document.getElementById('matches-matrix-view');
    const datesView = document.getElementById('matches-dates-view');
    const btnList = document.getElementById('btn-view-list');
    const btnMatrix = document.getElementById('btn-view-matrix');
    const btnDates = document.getElementById('btn-view-dates');

    // Reset all views
    listView.classList.add('hidden');
    matrixView.classList.add('hidden');
    datesView.classList.add('hidden');

    // Reset all buttons
    [btnList, btnMatrix, btnDates].forEach(btn => {
        if (btn) {
            btn.classList.remove('bg-primary', 'text-white');
            btn.classList.add('text-white/60', 'hover:text-white');
        }
    });

    if (view === 'list') {
        listView.classList.remove('hidden');
        btnList.classList.remove('text-white/60', 'hover:text-white');
        btnList.classList.add('bg-primary', 'text-white');
    } else if (view === 'matrix') {
        matrixView.classList.remove('hidden');
        btnMatrix.classList.remove('text-white/60', 'hover:text-white');
        btnMatrix.classList.add('bg-primary', 'text-white');
    } else if (view === 'dates') {
        datesView.classList.remove('hidden');
        btnDates.classList.remove('text-white/60', 'hover:text-white');
        btnDates.classList.add('bg-primary', 'text-white');
    }

    // Save preference
    localStorage.setItem('matchView', view);
}

function toggleDateCollapse(id) {
    const el = document.getElementById(id);
    const icon = document.getElementById('icon-' + id);
    if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        el.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

function openMatrixModal(cellData) {
    const modal = document.getElementById('matrixMatchModal');
    const home = window.teamsData[cellData.home_id];
    const away = window.teamsData[cellData.away_id];

    // Populate Header
    document.getElementById('matrix_home_name').textContent = home.name;
    document.getElementById('matrix_away_name').textContent = away.name;

    const homeShieldEl = document.getElementById('matrix_home_shield');
    const awayShieldEl = document.getElementById('matrix_away_shield');

    if (home.shield_url) {
        homeShieldEl.src = home.shield_url;
        homeShieldEl.classList.remove('hidden');
        if (homeShieldEl.parentElement.querySelector('div')) homeShieldEl.parentElement.querySelector('div').remove();
    } else {
        homeShieldEl.classList.add('hidden');
        // Add placeholder if not exists
        if (!homeShieldEl.parentElement.querySelector('div')) {
            const ph = document.createElement('div');
            ph.className = 'w-12 h-12 bg-white/10 rounded flex items-center justify-center';
            ph.innerHTML = '<i class="fas fa-shield-alt text-white/40"></i>';
            homeShieldEl.parentElement.insertBefore(ph, homeShieldEl);
        }
    }

    if (away.shield_url) {
        awayShieldEl.src = away.shield_url;
        awayShieldEl.classList.remove('hidden');
        if (awayShieldEl.parentElement.querySelector('div')) awayShieldEl.parentElement.querySelector('div').remove();
    } else {
        awayShieldEl.classList.add('hidden');
        if (!awayShieldEl.parentElement.querySelector('div')) {
            const ph = document.createElement('div');
            ph.className = 'w-12 h-12 bg-white/10 rounded flex items-center justify-center';
            ph.innerHTML = '<i class="fas fa-shield-alt text-white/40"></i>';
            awayShieldEl.parentElement.insertBefore(ph, awayShieldEl);
        }
    }

    document.getElementById('matrix_home_team_id').value = cellData.home_id;
    document.getElementById('matrix_away_team_id').value = cellData.away_id;
    document.getElementById('matrix_match_round').value = cellData.round || 1;

    const deleteBtn = document.getElementById('btn-delete-matrix-match');

    if (cellData.match) {
        // Edit Mode
        document.getElementById('matrix_match_id').value = cellData.match.id;

        // Format Date
        if (cellData.match.match_date_iso) {
            // ISO string is YYYY-MM-DDTHH:MM:SS
            const parts = cellData.match.match_date_iso.split('T');
            if (parts.length > 0) document.getElementById('matrix_match_date').value = parts[0];
            if (parts.length > 1) document.getElementById('matrix_match_time').value = parts[1].substring(0, 5); // HH:MM
        }

        document.getElementById('matrix_court_id').value = cellData.match.court_id || '';
        document.getElementById('matrix_home_score').value = cellData.match.home_score;
        document.getElementById('matrix_away_score').value = cellData.match.away_score;

        deleteBtn.classList.remove('hidden');
    } else {
        // Create Mode
        document.getElementById('matrix_match_id').value = '';
        document.getElementById('matrix_match_date').value = '';
        document.getElementById('matrix_match_time').value = '';
        document.getElementById('matrix_court_id').value = '';
        document.getElementById('matrix_home_score').value = '';
        document.getElementById('matrix_away_score').value = '';

        deleteBtn.classList.add('hidden');
    }

    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeMatrixModal() {
    document.getElementById('matrixMatchModal').classList.add('hidden');
    document.getElementById('matrixMatchModal').classList.remove('flex');
}

function showMatrixRound(round) {
    // Hide all rounds
    document.querySelectorAll('.matrix-round-container').forEach(el => el.classList.add('hidden'));

    // Show selected
    const selected = document.getElementById(`matrix-round-${round}`);
    if (selected) selected.classList.remove('hidden');

    // Update buttons
    // Reset all
    const allBtns = document.querySelectorAll('[id^="btn-matrix-round-"]');
    allBtns.forEach(btn => {
        btn.classList.remove('bg-primary', 'text-white');
        btn.classList.add('bg-white/5', 'text-white/60', 'hover:bg-white/10');
    });

    // Activate selected
    const activeBtn = document.getElementById(`btn-matrix-round-${round}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-white/5', 'text-white/60', 'hover:bg-white/10');
        activeBtn.classList.add('bg-primary', 'text-white');
    }
}

function confirmDelete() {
    if (confirm('¿Estás seguro de eliminar este partido? Se eliminarán los puntos otorgados.')) {
        document.getElementById('deleteMatchForm').submit();
    }
}

// Call the dataTables jQuery plugin

$(document).ready(function() {
  $('#dataTable').DataTable({
    "lengthChange": false,
    "pageLength": 20,
    "paging": false,
    "info": false,
    "ordering": false,
  });

  $('#reportDataTable').DataTable();
});

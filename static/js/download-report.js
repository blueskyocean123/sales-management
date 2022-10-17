// download sales report
var downloadReportPDF = document.getElementById('downloadReportPDF')
downloadReportPDF.addEventListener('click', (key, value) => {
    let url = new URL(window.document.location);
    let params = new URLSearchParams(url.search.slice(1));

    params.append('download', 'download')   
    window.location.search = params.toString();
    console.log(params);

    // if (params.has(key)) {
    //     params.set('download', 'download');
    // }else {
    //     params.append('download', 'download');
    // }
})




document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    app.innerHTML = `
        <h1>Hello, SPA!</h1>
        <button id="fetch-data">Fetch Data</button>
        <div id="data"></div>
    `;

    // document.getElementById('fetch-data').addEventListener('click', () => {
    //     fetch('/api/some-endpoint')
    //         .then(response => response.json())
    //         .then(data => {
    //             document.getElementById('data').innerHTML = JSON.stringify(data);
    //         });
    // });
});

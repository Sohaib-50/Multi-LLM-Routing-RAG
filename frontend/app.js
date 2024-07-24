document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    app.innerHTML = `
        <h1>Hello, SPA!</h1>
        <button id="fetch-data">Fetch Data</button>
        <div id="data"></div>
    `;

    document.getElementById('fetch-data').addEventListener('click', () => {
        fetch('/api/example')
            // log stringified response withou parsing
            .then(response => response.text())
            .then(data => {
                console.log(data);
                document.getElementById('data').innerHTML = data;
            });
    }
    );

});
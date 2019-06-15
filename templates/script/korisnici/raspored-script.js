function filter() {
    const input = document.getElementById("filter");

    const table = document.getElementById("table");

    const tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        tr[i].style.display = "none";

        let td = tr[i].getElementsByTagName("td");

        for (let j = 0; j < td.length; j++) {
            let cell = tr[i].getElementsByTagName("td")[j];

            if (cell) {
                if (cell.innerHTML.indexOf(input.value) > -1) {
                    tr[i].style.display = "";
                    break;
                }
            }
        }
    }
}
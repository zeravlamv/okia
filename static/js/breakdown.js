(function () {
  var dataNode = document.getElementById("breakdown-data");
  var root = document.getElementById("breakdown");
  if (!dataNode || !root) {
    return;
  }
  var sections = JSON.parse(dataNode.textContent);
  sections.forEach(function (section) {
    var title = document.createElement("h2");
    title.textContent = section.title;
    var table = document.createElement("table");
    var headRow = document.createElement("tr");
    ["Grupo", "Precio de venta"].forEach(function (label) {
      var cell = document.createElement("th");
      cell.textContent = label;
      headRow.appendChild(cell);
    });
    var head = document.createElement("thead");
    head.appendChild(headRow);
    table.appendChild(head);
    var body = document.createElement("tbody");
    section.rows.forEach(function (row) {
      var line = document.createElement("tr");
      [row.label, row.amount].forEach(function (value) {
        var cell = document.createElement("td");
        cell.textContent = value;
        line.appendChild(cell);
      });
      body.appendChild(line);
    });
    table.appendChild(body);
    root.appendChild(title);
    root.appendChild(table);
  });
})();

(function () {
  var dataNode = document.getElementById("hierarchy-data");
  var root = document.getElementById("hierarchy");
  var projects = [];
  var seenProjects = {};
  var data = { nodes: [], aside: [] };
  if (dataNode) {
    data = JSON.parse(dataNode.textContent);
    collectProjects(data.nodes || [], projects, seenProjects);
    (data.projects || []).forEach(function (item) {
      if (item && item.code && !seenProjects[item.code]) {
        seenProjects[item.code] = true;
        projects.push({ code: item.code, label: item.label || item.code });
      }
    });
  }
  var columns = [
    ["sales", "Ventas"],
    ["income", "Ingresos"],
    ["purchases", "Compras"],
    ["expenses", "Gastos"],
    ["margin", "Margen"],
    ["margin_percent", "%"]
  ];

  function visibleColumns(nodes) {
    var present = {};
    nodes.forEach(function (node) {
      columns.forEach(function (column) {
        if (Object.prototype.hasOwnProperty.call(node, column[0])) {
          present[column[0]] = column[1];
        }
      });
    });
    return columns.filter(function (column) {
      return present[column[0]];
    });
  }

  function renderLevel(nodes, container, ancestors) {
    if (!nodes.length) {
      return;
    }
    ancestors = ancestors || [];
    var heading = document.createElement("h2");
    heading.textContent = nodes[0].level;
    container.appendChild(heading);
    var shown = visibleColumns(nodes);
    var table = document.createElement("table");
    table.className = "table table-sm table-hover fiche-table";
    var headRow = document.createElement("tr");
    var headLabels = ["Grupo"].concat(shown.map(function (column) {
      return column[1];
    }));
    headLabels.forEach(function (label, index) {
      var cell = document.createElement("th");
      cell.textContent = label;
      if (index > 0) {
        cell.className = "amount";
      }
      headRow.appendChild(cell);
    });
    var head = document.createElement("thead");
    head.appendChild(headRow);
    table.appendChild(head);
    var body = document.createElement("tbody");
    nodes.forEach(function (node) {
      var trail = ancestors.concat([{ level: node.level, label: node.label }]);
      var line = document.createElement("tr");
      var nameCell = document.createElement("td");
      if (node.children.length) {
        var button = document.createElement("button");
        button.type = "button";
        button.textContent = node.label;
        button.setAttribute("aria-expanded", "false");
        nameCell.appendChild(button);
      } else {
        nameCell.textContent = node.label;
      }
      if (node.incomplete) {
        var mark = document.createElement("span");
        mark.className = "incomplete";
        mark.textContent = " Incompleto";
        nameCell.appendChild(mark);
      }
      if (node.level === "Proyecto" && node.code) {
        var fiche = document.createElement("a");
        fiche.href = "/proyecto/" + encodeURIComponent(node.code) + "/";
        fiche.textContent = "Ficha";
        nameCell.appendChild(document.createTextNode(" "));
        nameCell.appendChild(fiche);
      }
      line.appendChild(nameCell);
      shown.forEach(function (column) {
        var cell = document.createElement("td");
        cell.className = "amount";
        var value = node[column[0]];
        if (column[0] === "income" && node.label === "Sin dato" && value && value !== "0,00 EUR" && value !== "—") {
          var opener = document.createElement("button");
          opener.type = "button";
          opener.className = "amount-link";
          opener.setAttribute("data-kind", "arbol-ingreso");
          opener.setAttribute("data-path", JSON.stringify(trail));
          opener.textContent = value;
          cell.appendChild(opener);
        } else {
          cell.textContent = value;
        }
        line.appendChild(cell);
      });
      body.appendChild(line);
      if (node.children.length) {
        var childRow = document.createElement("tr");
        var childCell = document.createElement("td");
        childCell.colSpan = headLabels.length;
        var childBox = document.createElement("div");
        childBox.className = "tree-children";
        childBox.hidden = true;
        renderLevel(node.children, childBox, trail);
        childCell.appendChild(childBox);
        childRow.appendChild(childCell);
        body.appendChild(childRow);
        nameCell.querySelector("button").addEventListener("click", function () {
          var open = this.getAttribute("aria-expanded") === "true";
          this.setAttribute("aria-expanded", open ? "false" : "true");
          childBox.hidden = open;
        });
      }
    });
    table.appendChild(body);
    container.appendChild(table);
  }

  if (root) {
    renderLevel(data.nodes || [], root);
    bindTreeIncome(root);
  }
  if (root && data.aside && data.aside.length) {
    var asideTitle = document.createElement("h2");
    asideTitle.textContent = "Pedidos fuera de la jerarquía";
    root.appendChild(asideTitle);
    var asideTable = document.createElement("table");
    asideTable.className = "fiche-table";
    var asideHead = document.createElement("tr");
    ["Pedido", "Precio de venta"].forEach(function (label, index) {
      var cell = document.createElement("th");
      cell.textContent = label;
      if (index > 0) {
        cell.className = "amount";
      }
      asideHead.appendChild(cell);
    });
    var asideHeadBox = document.createElement("thead");
    asideHeadBox.appendChild(asideHead);
    asideTable.appendChild(asideHeadBox);
    var asideBody = document.createElement("tbody");
    data.aside.forEach(function (row) {
      var line = document.createElement("tr");
      var identity = document.createElement("td");
      identity.textContent = row.identity;
      var amount = document.createElement("td");
      amount.className = "amount";
      amount.textContent = row.amount;
      line.appendChild(identity);
      line.appendChild(amount);
      asideBody.appendChild(line);
    });
    asideTable.appendChild(asideBody);
    root.appendChild(asideTable);
  }
  bindFinder(projects);
})();

function bindTreeIncome(root) {
  var dialog = document.getElementById("tree-income");
  if (!dialog) {
    return;
  }
  var title = document.getElementById("tree-income-title");
  var source = document.getElementById("tree-income-source");
  var body = document.getElementById("tree-income-body");
  var total = document.getElementById("tree-income-total");

  function cellText(value) {
    var cell = document.createElement("td");
    cell.textContent = value;
    return cell;
  }

  function show(payload) {
    title.textContent = payload.title || "Ingresos";
    source.textContent = payload.source ? "Origen: " + payload.source : "";
    body.replaceChildren();
    total.textContent = "";
    if (payload.pending) {
      var pending = document.createElement("p");
      pending.textContent = payload.message;
      body.appendChild(pending);
      dialog.showModal();
      return;
    }
    if (!payload.rows || !payload.rows.length) {
      var empty = document.createElement("p");
      empty.textContent = "No hay apuntes en esta rama.";
      body.appendChild(empty);
      dialog.showModal();
      return;
    }
    var table = document.createElement("table");
    table.className = "table table-sm evolution-values";
    var head = document.createElement("tr");
    payload.headers.forEach(function (label) {
      var cell = document.createElement("th");
      cell.textContent = label;
      head.appendChild(cell);
    });
    var thead = document.createElement("thead");
    thead.appendChild(head);
    var tbody = document.createElement("tbody");
    payload.rows.forEach(function (row) {
      var line = document.createElement("tr");
      row.forEach(function (value) {
        line.appendChild(cellText(value));
      });
      tbody.appendChild(line);
    });
    table.appendChild(thead);
    table.appendChild(tbody);
    body.appendChild(table);
    total.textContent = payload.total ? "Total " + payload.total : "";
    dialog.showModal();
  }

  function fail() {
    show({
      title: "Ingresos",
      source: "",
      pending: true,
      message: "No se ha podido abrir el detalle.",
      rows: []
    });
  }

  root.addEventListener("click", function (event) {
    var button = event.target.closest("[data-kind='arbol-ingreso']");
    if (!button) {
      return;
    }
    var url = root.getAttribute("data-income-url") + "?ruta=" + encodeURIComponent(button.getAttribute("data-path"));
    var month = root.getAttribute("data-income-month");
    if (month) {
      url += "&mes=" + encodeURIComponent(month);
    }
    fetch(url, { headers: { "Accept": "application/json" } }).then(function (response) {
      if (!response.ok) {
        throw new Error("detalle");
      }
      return response.json();
    }).then(show).catch(fail);
  });
  dialog.querySelector("[data-close-tree]").addEventListener("click", function () {
    dialog.close();
  });
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) {
      dialog.close();
    }
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && dialog.open) {
      dialog.close();
      event.preventDefault();
    }
  });
}

function collectProjects(nodes, found, seen) {
  nodes.forEach(function (node) {
    if (node.level === "Proyecto" && node.code && !seen[node.code]) {
      seen[node.code] = true;
      found.push({ code: node.code, label: node.label || node.code });
    }
    if (node.children && node.children.length) {
      collectProjects(node.children, found, seen);
    }
  });
}

function bindFinder(projects) {
  var form = document.getElementById("project-finder");
  var input = document.getElementById("project-query");
  var list = document.getElementById("project-matches");
  if (!form || !input || !list) {
    return;
  }

  function openFiche(code) {
    if (!code) {
      return;
    }
    window.location.href = "/proyecto/" + encodeURIComponent(code) + "/";
  }

  function matches(query) {
    var needle = query.trim().toLocaleLowerCase();
    if (!needle) {
      return [];
    }
    return projects.filter(function (item) {
      return item.code.toLocaleLowerCase().indexOf(needle) !== -1 || item.label.toLocaleLowerCase().indexOf(needle) !== -1;
    });
  }

  function show(found) {
    list.innerHTML = "";
    if (!found.length) {
      list.hidden = true;
      return;
    }
    var visible = found.slice(0, 8);
    visible.forEach(function (item) {
      var line = document.createElement("li");
      var link = document.createElement("a");
      link.href = "/proyecto/" + encodeURIComponent(item.code) + "/";
      link.textContent = item.label;
      line.appendChild(link);
      list.appendChild(line);
    });
    if (found.length > visible.length) {
      var more = document.createElement("li");
      more.className = "hint";
      more.textContent = "Hay más proyectos. Afina el texto.";
      list.appendChild(more);
    }
    list.hidden = false;
  }

  input.addEventListener("input", function () {
    show(matches(input.value));
  });
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var query = input.value.trim();
    if (!query) {
      return;
    }
    var code = query.split(" — ")[0].trim();
    var exact = projects.filter(function (item) {
      return item.code.toLocaleLowerCase() === code.toLocaleLowerCase();
    });
    if (exact.length === 1) {
      openFiche(exact[0].code);
      return;
    }
    var found = matches(query);
    if (found.length === 1) {
      openFiche(found[0].code);
      return;
    }
    if (!found.length) {
      openFiche(code);
      return;
    }
    show(found);
  });
}

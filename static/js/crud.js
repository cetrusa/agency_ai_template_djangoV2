/*
CRUD UI KIT JS (mínimo)

Objetivo:
- UX de selección masiva (select-all, contador, ids)
- Cerrar modal bootstrap tras éxito (disparado por HX-Trigger)

No hace SPA, no maneja negocio.
*/

(function () {
  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $all(sel, root) {
    return Array.from((root || document).querySelectorAll(sel));
  }

  function getSelectedIds() {
    return $all("[data-crud-row-check]:checked").map((el) => el.value);
  }

  function syncBulkUI() {
    const bulk = $("[data-crud-bulk]");
    if (!bulk) return;

    const ids = getSelectedIds();
    const countEl = $("[data-crud-selected-count]");
    const idsEl = $("[data-crud-selected-ids]");

    if (countEl) countEl.textContent = String(ids.length);
    if (idsEl) idsEl.value = ids.join(",");

    bulk.hidden = ids.length === 0;
  }

  function bindSelectionHandlers(root) {
    const scope = root || document;

    const selectAll = $("[data-crud-select-all]", scope);
    if (selectAll) {
      selectAll.addEventListener("change", () => {
        const isChecked = selectAll.checked;
        $all("[data-crud-row-check]", document).forEach((cb) => {
          cb.checked = isChecked;
        });
        syncBulkUI();
      });
    }

    $all("[data-crud-row-check]", scope).forEach((cb) => {
      cb.addEventListener("change", () => {
        // Mantén el checkbox maestro en estado consistente.
        const allChecks = $all("[data-crud-row-check]", document);
        const checked = allChecks.filter((x) => x.checked);
        if (selectAll) {
          selectAll.indeterminate = checked.length > 0 && checked.length < allChecks.length;
          selectAll.checked = checked.length === allChecks.length && allChecks.length > 0;
        }
        syncBulkUI();
      });
    });

    const clearBtn = $("[data-crud-clear-selection]", scope);
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        $all("[data-crud-row-check]", document).forEach((cb) => {
          cb.checked = false;
        });
        if (selectAll) {
          selectAll.checked = false;
          selectAll.indeterminate = false;
        }
        syncBulkUI();
      });
    }

    syncBulkUI();
  }

  function closeBootstrapModal(modalId) {
    const el = document.getElementById(modalId);
    if (!el || !window.bootstrap) return;

    const instance = window.bootstrap.Modal.getInstance(el) || new window.bootstrap.Modal(el);
    instance.hide();
  }

  // Re-bindea tras swaps HTMX (tabla/paginación/filtros).
  document.body.addEventListener("htmx:afterSwap", (evt) => {
    const target = evt.detail && evt.detail.target;
    // Si se actualiza la tabla, vuelve a enganchar eventos de selección.
    if (target && (target.id === "crud-table" || target.closest && target.closest("#crud-table"))) {
      bindSelectionHandlers(document);
    }
  });

  // Eventos disparados por el backend vía HX-Trigger.
  document.body.addEventListener("crudModalClose", () => {
    closeBootstrapModal("appModal");
  });

  // Init inicial.
  bindSelectionHandlers(document);
})();

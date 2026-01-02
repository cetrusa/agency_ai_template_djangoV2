/*
Modal System JS (mínimo)

Responsabilidades:
- Abrir/cerrar: limpiar el #modal-host
- Escape para cerrar
- Click en backdrop (configurable)
- Focus trap básico
- Bloqueo de scroll en body
- Integración HTMX (re-init tras swap)

Eventos soportados:
- document.dispatchEvent(new Event('modalClose'))
- document.dispatchEvent(new Event('crudModalClose')) (compat)
- HX-Trigger desde backend: {"modalClose": true}

No maneja lógica de negocio.
*/

(function () {
  const hostId = "modal-host";
  let lastFocused = null;

  function host() {
    return document.getElementById(hostId);
  }

  function isOpen() {
    const h = host();
    return !!(h && h.querySelector("[data-modal]"));
  }

  function getPanel() {
    const h = host();
    return h ? h.querySelector(".ds-modal__panel") : null;
  }

  function getFocusable(root) {
    if (!root) return [];
    const selectors = [
      "a[href]",
      "button:not([disabled])",
      "textarea:not([disabled])",
      "input:not([disabled])",
      "select:not([disabled])",
      "[tabindex]:not([tabindex='-1'])",
    ].join(",");
    return Array.from(root.querySelectorAll(selectors)).filter((el) => {
      const style = window.getComputedStyle(el);
      return style.visibility !== "hidden" && style.display !== "none";
    });
  }

  function openInit() {
    if (!isOpen()) return;

    document.body.classList.add("ds-modal-open");
    lastFocused = document.activeElement;

    const panel = getPanel();
    if (panel) {
      // Enfoca el primer elemento interactivo.
      const focusables = getFocusable(panel);
      (focusables[0] || panel).focus();
    }
  }

  function closeModal() {
    const h = host();
    if (!h) return;

    h.innerHTML = "";
    document.body.classList.remove("ds-modal-open");

    // Restore focus.
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
    lastFocused = null;
  }

  function backdropAllowsClose() {
    const h = host();
    const modal = h ? h.querySelector("[data-modal]") : null;
    if (!modal) return true;
    return modal.getAttribute("data-backdrop-close") !== "0";
  }

  // Click-to-close
  document.addEventListener("click", (e) => {
    // Botones explícitos
    const closeBtn = e.target.closest("[data-action='close-modal']");
    if (closeBtn) {
      e.preventDefault();
      closeModal();
      return;
    }

    const submitBtn = e.target.closest("[data-action='submit-modal-form']");
    if (submitBtn) {
      const selector = submitBtn.getAttribute("data-form-selector") || ".ds-modal-form";
      const h = host();
      const form = h ? h.querySelector(selector) : null;
      if (form && typeof form.requestSubmit === "function") {
        form.requestSubmit();
      } else if (form) {
        form.submit();
      }
      return;
    }

    // Backdrop
    const backdrop = e.target.closest("[data-modal-backdrop]");
    if (backdrop && backdropAllowsClose()) {
      closeModal();
    }
  });

  // Escape + focus trap
  document.addEventListener("keydown", (e) => {
    if (!isOpen()) return;

    if (e.key === "Escape") {
      if (backdropAllowsClose()) {
        e.preventDefault();
        closeModal();
      }
      return;
    }

    if (e.key !== "Tab") return;

    const panel = getPanel();
    const focusables = getFocusable(panel);
    if (focusables.length === 0) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

  // HTMX hooks
  document.body.addEventListener("htmx:afterSwap", (evt) => {
    const target = evt.detail && evt.detail.target;
    if (target && target.id === hostId) {
      openInit();
    }
  });

  document.body.addEventListener("htmx:beforeSwap", (evt) => {
    // Si el backend decide limpiar el host devolviendo vacío.
    const target = evt.detail && evt.detail.target;
    if (target && target.id === hostId && !evt.detail.xhr.responseText) {
      closeModal();
    }
  });

  // Eventos disparados por HX-Trigger o JS.
  document.body.addEventListener("modalClose", closeModal);
  document.body.addEventListener("crudModalClose", closeModal);

  // Init (por si el server renderiza un modal directo).
  openInit();
})();

/* Little Lemon frontend — talks to the real API endpoints. */

const TOKEN_KEY = "littlelemon_token";
const $ = (id) => document.getElementById(id);

/* ---------------- response log ---------------- */

function log(status, message, body) {
  const line = document.createElement("div");
  line.className = "log-line";
  const cls = status >= 200 && status < 300 ? "tag-2xx" : "tag-4xx";
  line.innerHTML =
    `<span class="${cls}">${status}</span> &nbsp;${message}` +
    (body ? `<br><span style="color:#8f8fa5">${escapeHtml(body)}</span>` : "");
  $("log").prepend(line);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text).slice(0, 300);
  return div.innerHTML;
}

/* ---------------- booking result banner ---------------- */

function showBanner(kind, title, detail) {
  const el = $("booking-result");
  el.className = "result " + kind; // ok | dup | auth | err
  el.innerHTML = `<b>${title}</b><span>${detail}</span>`;
}

function hideBanner() {
  $("booking-result").classList.add("hidden");
}

$("clear-log").addEventListener("click", () => {
  $("log").innerHTML = '<div class="log-line muted">Cleared.</div>';
});

/* ---------------- menu ---------------- */

async function loadMenu() {
  try {
    const res = await fetch("/restaurant/menu/");
    log(res.status, "GET /restaurant/menu/");
    const data = await res.json();
    const items = Array.isArray(data) ? data : data.results;
    const grid = $("menu-grid");
    grid.innerHTML = "";
    items.forEach((item) => {
      grid.insertAdjacentHTML(
        "beforeend",
        `<div class="dish">
           <div class="dish-img">🥗</div>
           <div class="dish-body">
             <h3>${escapeHtml(item.title)}</h3>
             <div class="dish-meta">
               <span class="price">$${item.price}</span>
               <span class="stock">${item.inventory} in stock</span>
             </div>
           </div>
         </div>`
      );
    });
  } catch (err) {
    $("menu-grid").innerHTML =
      '<div class="skeleton">Could not reach the API — is the server running?</div>';
  }
}

/* ---------------- auth ---------------- */

function setSignedIn(username, token) {
  localStorage.setItem(TOKEN_KEY, token);
  const state = $("auth-state");
  state.textContent = `✓ Signed in as ${username} — token stored`;
  state.classList.add("signed-in");
}

function setSignedOut() {
  localStorage.removeItem(TOKEN_KEY);
  const state = $("auth-state");
  state.textContent = "Not signed in — bookings will be rejected (401)";
  state.classList.remove("signed-in");
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document
      .querySelectorAll(".tab")
      .forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    $("login-form").classList.toggle("hidden", tab.dataset.tab !== "login");
    $("register-form").classList.toggle("hidden", tab.dataset.tab !== "register");
  });
});

$("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = $("register-username").value.trim();
  const password = $("register-password").value;
  const res = await fetch("/auth/users/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const body = await res.text();
  log(res.status, `POST /auth/users/ (${username})`, body);
  if (res.status === 201) {
    // Auto-login after successful registration.
    const login = await fetch("/auth/token/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (login.status === 200) {
      const data = await login.json();
      setSignedIn(username, data.auth_token);
      log(login.status, "POST /auth/token/login/", login.responseText);
      loadMyBookings();
    }
  }
});

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = $("login-username").value.trim();
  const password = $("login-password").value;
  const res = await fetch("/auth/token/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  log(res.status, `POST /auth/token/login/ (${username})`, res.responseText);
  if (res.status === 200) {
    setSignedIn(username, data.auth_token);
    loadMyBookings();
  }
});

/* ---------------- bookings ---------------- */

function bookingPayload() {
  return {
    name: $("bk-name").value.trim() || "Guest",
    no_of_guests: Number($("bk-guests").value),
    table_number: Number($("bk-table").value),
    booking_date: $("bk-date").value ? $("bk-date").value + ":00" : "",
  };
}

async function createBooking() {
  const payload = bookingPayload();
  const token = localStorage.getItem(TOKEN_KEY);
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Token ${token}`;
  hideBanner();

  const res = await fetch("/restaurant/booking/tables/", {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const body = await res.text();
  const note =
    res.status === 401
      ? " ← no/invalid token"
      : res.status === 201
        ? " ← table reserved!"
        : res.status === 400
          ? " ← double booking blocked by unique constraint"
          : "";
  log(res.status, `POST /restaurant/booking/tables/ (table ${payload.table_number})${note}`, body);

  // Big, obvious banner in the booking card.
  if (res.status === 201) {
    showBanner(
      "ok",
      `✓ Table ${payload.table_number} reserved for ${payload.name}!`,
      `Saved in MySQL: ${payload.no_of_guests} guest(s), ${payload.booking_date}.`
    );
    loadMyBookings();
  } else if (res.status === 400) {
    showBanner(
      "dup",
      "✗ Double booking blocked!",
      `Table ${payload.table_number} is already reserved at ${payload.booking_date}. The unique constraint refused it — nothing was saved.`
    );
  } else if (res.status === 401) {
    showBanner(
      "auth",
      "✗ Not signed in (401)",
      "You need a token to book. Log in on the left, then try again."
    );
  } else {
    showBanner("err", `✗ Unexpected response ${res.status}`, body);
  }
}

$("booking-form").addEventListener("submit", (e) => {
  e.preventDefault();
  createBooking();
});

$("btn-rebook").addEventListener("click", () => createBooking());

/* ---------------- my bookings list ---------------- */

async function loadMyBookings() {
  const wrap = $("bookings-table-wrap");
  const token = localStorage.getItem(TOKEN_KEY);

  if (!token) {
    wrap.innerHTML =
      '<div class="log-line muted">Sign in to see your saved bookings.</div>';
    return;
  }

  const res = await fetch("/restaurant/booking/tables/", {
    headers: { Authorization: `Token ${token}` },
  });

  if (res.status !== 200) {
    wrap.innerHTML =
      '<div class="log-line muted">Could not load bookings (is the token still valid? log in again).</div>';
    return;
  }

  const data = await res.json();
  const items = Array.isArray(data) ? data : data.results;

  if (!items.length) {
    wrap.innerHTML =
      '<div class="log-line muted">No bookings yet — reserve a table above and it will appear here.</div>';
    return;
  }

  const rows = items
    .map(
      (b) => `<tr>
        <td>#${b.id}</td>
        <td>${escapeHtml(b.name)}</td>
        <td>${b.no_of_guests} guest(s)</td>
        <td>Table ${b.table_number}</td>
        <td>${escapeHtml(String(b.booking_date).replace("T", " ").slice(0, 16))} UTC</td>
      </tr>`
    )
    .join("");
  wrap.innerHTML = `
    <table class="mini-table">
      <thead><tr><th>ID</th><th>Name</th><th>Party</th><th>Table</th><th>When</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

$("refresh-bookings").addEventListener("click", loadMyBookings);

/* ---------------- init ---------------- */

(function init() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    const state = $("auth-state");
    state.textContent = "✓ Signed in — token restored from this browser";
    state.classList.add("signed-in");
  }
  // Default the datetime field to tomorrow 19:00 for a nice demo.
  const d = new Date(Date.now() + 24 * 60 * 60 * 1000);
  d.setHours(19, 0, 0, 0);
  $("bk-date").value = d.toISOString().slice(0, 16);
  $("bk-name").value = "Niraj";
  loadMenu();
  loadMyBookings();
})();
